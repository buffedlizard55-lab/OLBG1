#!/usr/bin/env python3
"""Validate TB2719 data, High gates, generated HTML and local links."""
from __future__ import annotations

import json
import math
import re
import shutil
from collections import Counter
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "b2719ad3"
SITE = ROOT / "b2719ad3"
OBS = json.loads((DATA / "observations.json").read_text(encoding="utf-8"))
PRICES = json.loads((DATA / "prices.json").read_text(encoding="utf-8"))
PREDICTIONS = json.loads((DATA / "predictions.json").read_text(encoding="utf-8"))
SOURCES = OBS["source_registry"]
EXPECTED = ["golf", "volleyball", "rugby-union", "cricket", "snooker", "darts", "baseball", "gaelic-sports", "greyhounds", "tennis", "motor-racing", "handball", "ice-hockey", "basketball", "rugby-league"]
checks: list[dict] = []


def check(name: str, condition: bool, detail: str = "") -> None:
    checks.append({"name": name, "passed": bool(condition), "detail": detail})


def american_value(p: float) -> int:
    raw = -100 * p / (1 - p) if p >= 0.5 else 100 * (1 - p) / p
    return int(round(raw))


def words(text: str) -> int:
    return len(re.findall(r"\b[\w’'-]+\b", text, re.UNICODE))


class Links(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if tag == "a" and values.get("href"):
            self.links.append(values["href"])
        if tag == "link" and values.get("href"):
            self.links.append(values["href"])


scope = [s["slug"] for s in OBS["scope"]]
check("exact fifteen-sport scope and order", scope == EXPECTED, ", ".join(scope))
check("scope has no duplicate sports", len(scope) == len(set(scope)) == 15)

ids = [e["id"] for e in OBS["events"]]
check("observation IDs are unique", len(ids) == len(set(ids)), f"{len(ids)} observations")
check("all event sports are in scope", all(e["sport"] in scope for e in OBS["events"]))
check("all event source IDs resolve", all(e["official_source"] in SOURCES and all(k in SOURCES for k in e["evidence_sources"]) for e in OBS["events"]))
check("all sources use valid HTTPS URLs", all(urlparse(s["url"]).scheme == "https" and urlparse(s["url"]).netloc for s in SOURCES.values()), f"{len(SOURCES)} sources")
check("no localhost source URLs", all("localhost" not in s["url"] and "127.0.0.1" not in s["url"] for s in SOURCES.values()))
check("unpriced observations carry review reasons", all(e.get("pricing") or e.get("flags") for e in OBS["events"]))
check("Williams-Jones UTC start remains blank", next(e for e in OBS["events"] if e["id"] == "snooker-williams-jones-20261024")["start_utc"] is None)
check("greyhound runner-level rows remain unpriced", all(not e.get("pricing") for e in OBS["events"] if e["sport"] == "greyhounds"))

as_of = datetime.fromisoformat(PRICES["as_of"].replace("Z", "+00:00"))
active = PRICES["active_rows"]
started = PRICES["started_rows"]
check("active and started rows partition observations", len(active) + len(started) == len(OBS["events"]), f"{len(active)} active + {len(started)} started")
check("started rows have no active analysis", all(r.get("analysis") is None for r in started))
check("all confirmed active starts are future at snapshot", all(not r.get("start_utc") or datetime.fromisoformat(r["start_utc"].replace("Z", "+00:00")) > as_of for r in active))
check("Anaheim-Philadelphia is excluded after its start", any(r["id"] == "nhl-2026020168" for r in started))

high = []
for r in active:
    a = r.get("analysis")
    if not a:
        check(f'unpriced row has flags: {r["id"]}', bool(r.get("flags")))
        continue
    p = a["probability"]
    check(f'probability range: {r["id"]}', 0 < p < 1)
    check(f'winner probabilities sum to one: {r["id"]}', math.isclose(sum(a["probabilities"].values()), 1.0, abs_tol=1e-9))
    check(f'fair American price recalculation: {r["id"]}', a["fair_american"] == american_value(p))
    check(f'selection is strongest winner outcome: {r["id"]}', a["selection_side"] == max(a["probabilities"], key=a["probabilities"].get))
    check(f'selection names an official participant: {r["id"]}', a["selection"] == r[a["selection_side"]])
    d = a.get("derivative")
    if d:
        check(f'over probability range: {r["id"]}', 0 < d["over_probability"] < 1)
        check(f'cover probability range: {r["id"]}', 0 < d["home_cover_probability"] < 1)
        check(f'over fair recalculation: {r["id"]}', d["over_fair_american"] == american_value(d["over_probability"]))
        check(f'cover fair recalculation: {r["id"]}', d["home_cover_fair_american"] == american_value(d["home_cover_probability"]))
    if a["grade"] == "High":
        high.append(r)
        check(f'High probability strictly above 70%: {r["id"]}', p > 0.70, f'{p:.8f}')
        check(f'High price in requested band: {r["id"]}', -250 <= a["fair_american"] <= 10000, str(a["fair_american"]))
        check(f'High sample gate: {r["id"]}', a["minimum_sample"] >= 6)
        check(f'High future start gate: {r["id"]}', bool(r.get("start_utc")))
        check(f'High availability gate: {r["id"]}', bool(r.get("availability", "").strip()))
        check(f'High prediction length: {r["id"]}', words(a["prediction"]) >= 30, f'{words(a["prediction"])} words')
        check(f'High prediction language: {r["id"]}', not re.search(r"\b(model|verified)\b", a["prediction"], re.I))
        check(f'High gate internally complete: {r["id"]}', all(a["high_gate"].values()) and not a["high_gate_failures"])

check("High predictions match High rows", len(PREDICTIONS) == len(high) == len(PRICES["high_prediction_ids"]), f"{len(high)} High")
check("no sport exceeds five High selections", all(n <= 5 for n in Counter(r["sport"] for r in high).values()), str(Counter(r["sport"] for r in high)))
normalized = [re.sub(r"\s+", " ", p["prediction"].strip().lower()) for p in PREDICTIONS]
check("High predictions are unique", len(normalized) == len(set(normalized)))
check("High prediction hashes are unique", len({p["sha256"] for p in PREDICTIONS}) == len(PREDICTIONS))
check("prediction JSON contains only full analysis", all(p["words"] >= 30 and p["prediction"] and p["official_source"].startswith("https://") for p in PREDICTIONS))
check("Edmonton boundary price remains exactly -250", any(r["id"] == "nhl-2026020176" and r["analysis"]["fair_american"] == -250 and r["analysis"]["grade"] == "High" for r in active))
check("New Jersey -267 is not forced into High band", any(r["id"] == "nhl-2026020169" and r["analysis"]["fair_american"] == -267 and r["analysis"]["grade"] != "High" for r in active))
check("Vegas exactly 70% is not High", any(r["id"] == "nhl-2026020174" and math.isclose(r["analysis"]["probability"], 0.70) and r["analysis"]["grade"] != "High" for r in active))

# Generated files, row-level official links and local navigation.
html_files = sorted(SITE.rglob("*.html"))
check("all fifteen sport subpages exist", all((SITE / "sports" / f"{s}.html").is_file() for s in EXPECTED))
check("required executive and review pages exist", all((SITE / name).is_file() for name in ("index.html", "sports.html", "flagged-for-review.html", "method.html")))
broken: list[str] = []
for file in html_files:
    parser = Links()
    text = file.read_text(encoding="utf-8")
    parser.feed(text)
    for href in parser.links:
        if href.startswith(("https://", "http://", "mailto:", "#", "data:")):
            continue
        clean = href.split("#", 1)[0].split("?", 1)[0]
        if not clean:
            continue
        target = (file.parent / clean).resolve()
        try:
            target.relative_to(ROOT)
        except ValueError:
            broken.append(f"{file.relative_to(ROOT)} -> outside repository: {href}")
            continue
        if not target.exists():
            broken.append(f"{file.relative_to(ROOT)} -> {href}")
    check(f'no serialized null/NaN values: {file.relative_to(ROOT)}', not re.search(r">\s*(?:None|nan|PENDING)\s*<", text))
check("all local HTML/CSS links resolve", not broken, "; ".join(broken[:10]))

for file in html_files:
    text = file.read_text(encoding="utf-8")
    fixture_rows = re.findall(r'<tr class="fixture-row".*?</tr>', text, re.S)
    check(f'every fixture row has an official link: {file.relative_to(ROOT)}', all('href="https://' in row and ">Official" in row for row in fixture_rows), f"{len(fixture_rows)} rows")
    derivative_rows = re.findall(r'<tr data-market-event=.*?</tr>', text, re.S)
    check(f'every derivative row has an official link: {file.relative_to(ROOT)}', all('href="https://' in row for row in derivative_rows), f"{len(derivative_rows)} rows")
    review_rows = re.findall(r'<tr data-review=.*?</tr>', text, re.S)
    check(f'every review row has a review link: {file.relative_to(ROOT)}', all('href="https://' in row for row in review_rows), f"{len(review_rows)} rows")

index_text = (SITE / "index.html").read_text(encoding="utf-8")
check("home page contains every active fixture row", len(re.findall(r'<tr class="fixture-row"', index_text)) == len(active))
method_text = (SITE / "method.html").read_text(encoding="utf-8")
check("method page contains every registered source", len(re.findall(r'<tr data-source-id=', method_text)) == len(SOURCES))
check("public machine-readable data copied", all((SITE / "data" / name).is_file() for name in ("observations.json", "prices.json", "predictions.json", "review.json", "build-report.json")))

report = {
    "desk": "TB2719",
    "checked_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
    "status": "PASS" if all(c["passed"] for c in checks) else "FAIL",
    "checks_passed": sum(c["passed"] for c in checks),
    "checks_total": len(checks),
    "active_rows": len(active),
    "started_exclusions": len(started),
    "high_predictions": len(high),
    "html_files": len(html_files),
    "broken_local_links": broken,
    "external_link_validation": "HTTPS syntax and source identity checked; evidence was captured with research tools. No claim of a fresh shell HTTP status sweep.",
    "checks": checks,
}
(DATA / "checks.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
(SITE / "data").mkdir(exist_ok=True)
shutil.copy2(DATA / "checks.json", SITE / "data" / "checks.json")
print(json.dumps({k: v for k, v in report.items() if k != "checks"}, indent=2))
if report["status"] != "PASS":
    for c in checks:
        if not c["passed"]:
            print(f'FAIL: {c["name"]} {c["detail"]}')
    raise SystemExit(1)
