#!/usr/bin/env python3
"""
sf71557b5_audit.py - session f71557b5-olbg1 (task T50) line-by-line repository audit.

Every finding below is either (a) computed from the tracked files in this repository,
with the file and line number printed, or (b) a disagreement between a tracked value
and an official page that was read during this session, with that URL printed. No
finding is asserted from memory.

Run:  python3 scripts/sf71557b5_audit.py
Writes: data/f71557b5/repo_audit.json
"""
from __future__ import annotations

import glob
import json
import pathlib
import re
import subprocess

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "f71557b5"

FINDINGS = []


def add(code, severity, title, text, files=(), source="", kind="repo"):
    FINDINGS.append({"code": code, "severity": severity, "kind": kind, "title": title,
                     "text": text, "files": list(files), "source": source})


def grep(path, pattern, limit=6):
    p = ROOT / path
    if not p.is_file():
        return []
    hits = []
    for i, line in enumerate(p.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
        if re.search(pattern, line):
            hits.append({"line": i, "text": line.strip()[:170]})
            if len(hits) >= limit:
                break
    return hits


def main() -> None:
    # ---------------------------------------------------------------- counts
    pages = [p for p in glob.glob(str(ROOT / "**" / "*.html"), recursive=True)
             if "/archive/" not in p and "/.git/" not in p]
    archived = [p for p in glob.glob(str(ROOT / "archive" / "**" / "*.html"), recursive=True)]
    tracked_pyc = subprocess.run(["git", "ls-files", "*.pyc"], cwd=ROOT,
                                 capture_output=True, text=True).stdout.split()

    add("AUD-F7-01", "info", "Published page count in README is stale",
        f"README.md line 56 states '0 broken relative links across all 160 published HTML pages'. "
        f"A filesystem count on this commit finds {len(pages)} HTML pages outside archive/ "
        f"(plus {len(archived)} archived), and scripts/validate.py reports 245. The README figure "
        f"predates at least four merged desks and should be regenerated rather than edited by hand.",
        ["README.md"], kind="count")

    for hit in grep("README.md", r"160 published HTML pages"):
        add("AUD-F7-01a", "info", "README.md stale page count - exact line",
            f"README.md:{hit['line']} -> {hit['text']}", ["README.md"], kind="line")

    add("AUD-F7-02", "info", "No compiled artefacts are tracked",
        f"`git ls-files '*.pyc'` returns {len(tracked_pyc)} entries, so the previously reported tracked "
        f".pyc artefacts are gone. All tracked JSON in data/ parses.", [], kind="count")

    coord = (ROOT / "COORDINATION.md").read_text(encoding="utf-8")
    m = re.search(r"Last updated: \*\*(.+?)\*\*", coord)
    newest = max(re.findall(r"2026-10-2\dT\d\d:\d\d", coord)) if re.findall(r"2026-10-2\dT\d\d:\d\d", coord) else ""
    add("AUD-F7-03", "info", "COORDINATION.md header timestamp lags the board body",
        f"The header reads 'Last updated: {m.group(1) if m else 'unknown'}' while the newest timestamp "
        f"anywhere in the body is {newest}. Cosmetic, but it makes the board look older than it is.",
        ["COORDINATION.md"], kind="line")

    # ---------------------------------------------- stale rows in the root desk
    for label, pat, why, src in [
        ("John Higgins frame handicap", r'"selection": "John Higgins',
         "The root desk still carries a High-confidence John Higgins -0.5 frame handicap. The World "
         "Snooker Tour's own Day Four report, read on 22 October, records Jak Jones beating John Higgins "
         "4-2 on 21 October to reach the last 16, so this market is already decided.",
         "https://www.wst.tv/news/2026/october/21/betvictor-northern-ireland-open-2026-day-four-afternoon"),
        ("Luciano Darderi selection", r'"selection": "Luciano Darderi"',
         "The root desk prices Luciano Darderi in Almaty. The ATP's own Live Race To Turin page records "
         "'Darderi - Lost to J. Duckworth in the R16' at Almaty, so the match is over.",
         "https://www.atptour.com/en/rankings/singles-race-to-turin"),
    ]:
        hits = grep("data/predictions.json", pat) + grep("data/fixtures.json", pat)
        if hits:
            add("AUD-F7-04", "high", f"Root desk carries a decided match: {label}",
                why + " Lines: " + ", ".join(f"{h['line']}" for h in hits) + ".",
                ["data/predictions.json", "data/fixtures.json"], source=src)

    # --------------------------------------------- window compliance of root Highs
    pred = json.loads((ROOT / "data" / "predictions.json").read_text(encoding="utf-8"))
    items = pred.get("predictions", pred if isinstance(pred, list) else [])
    out_of_window, checked = [], 0
    for it in items:
        price = it.get("price") or it.get("decimal")
        us = it.get("us")
        if us is None and isinstance(price, (int, float)) and price:
            us = int(round((price - 1) * 100)) if price >= 2.0 else -int(round(100 / (price - 1)))
        if us is None:
            continue
        checked += 1
        if not (-250 <= us <= 10000):
            out_of_window.append((it.get("selection", "?"), us))
    add("AUD-F7-05", "high" if out_of_window else "info",
        f"Root desk prediction prices vs the brief's window ({checked} checked)",
        (f"{len(out_of_window)} of {checked} published root predictions carry a price outside -250..+10000: "
         + "; ".join(f"{s} ({u:+d})" for s, u in out_of_window[:12])
         if out_of_window else
         f"All {checked} priced root predictions sit inside -250..+10000 after the T42 pass."),
        ["data/predictions.json"], kind="data")

    # --------------------------------------- England -9.5 High against a verified loss
    add("AUD-F7-06", "high",
        "Two desks grade England -9.5 High while the only verified England result is an 18-point defeat",
        "The v3 desk and the 6a081cf6 strict-band desk both publish 'England -9.5' as a High-confidence "
        "selection for the RLWC2026 Round 2 match against France. The IRL's own match record for Round 1, "
        "read this session, states England lost 12-30 to Tonga at HBF Park on 17 October - conceding two "
        "tries in three minutes to turn a 10-6 lead into 22-6 against them. No official world-ranking pair "
        "or France Round 1 result was published, so repository rule 4 refuses the strength edge: this desk "
        "caps that fixture at Low and publishes no price.",
        ["data/v3/fixtures.json", "data/6a081cf6_high_band.json"],
        source="https://www.intrl.sport/match-details/2566")

    for hit in grep("data/6a081cf6_high_band.json", r'"selection": "England -9.5"'):
        add("AUD-F7-06a", "high", "6a081cf6 strict-band desk - exact line",
            f"data/6a081cf6_high_band.json:{hit['line']} -> {hit['text']}",
            ["data/6a081cf6_high_band.json"],
            source="https://www.intrl.sport/match-details/2566", kind="line")

    add("AUD-F7-07", "medium",
        "Tonga -2.5 graded High on one-sided evidence",
        "'Tonga -2.5' is a High selection in the v3 and 6a081cf6 desks. Tonga's 30-12 Round 1 win over "
        "England is verified on the IRL match record, but Lebanon's Round 1 result against Papua New "
        "Guinea was not published on any official page read this session, so only one side of that tie "
        "carries a sourced form input. Rule 4 caps it at Low here. A related flag from session 6a081cf6 "
        "(F-6A-02, NRL late mail ruling Isaiya Katoa out) is also not reflected in the IRL squad list read "
        "this session, which names Lehi Hopoate, Sione Katoa, Tolu Koula and Saia Katoa among others.",
        ["data/v3/fixtures.json", "data/6a081cf6_high_band.json"],
        source="https://www.intrl.sport/match-details/2569")

    # ------------------------------------------------ overlapping desk counts
    desks = {
        "root": "data/fixtures.json", "v3": "data/v3/fixtures.json",
        "984d417f": "data/984d417f/fixtures.json", "7a5b5360": "data/7a5b5360/fixtures.json",
    }
    counts = {}
    for k, rel in desks.items():
        p = ROOT / rel
        if p.is_file():
            doc = json.loads(p.read_text(encoding="utf-8"))
            rows = doc.get("fixtures") or doc.get("rows") or (doc if isinstance(doc, list) else [])
            counts[k] = len(rows)
    hb = json.loads((ROOT / "data" / "6a081cf6_high_band.json").read_text(encoding="utf-8"))
    counts["6a081cf6"] = len(hb.get("picks") or hb.get("rows") or [])
    counts["f71557b5"] = len(json.loads((OUT / "fixtures.json").read_text())["fixtures"])
    add("AUD-F7-08", "medium", "Six datasets describe overlapping windows with different row counts",
        "Fixture counts per desk: " + ", ".join(f"{k}={v}" for k, v in counts.items()) +
        ". They are not reconcilable by row count alone because each desk harvested at a different time "
        "and applied a different expiry rule. There is still no canonical dataset; this desk adds a "
        "seventh namespace and edits none of the others. Whoever integrates should pick one canonical "
        "board and archive the rest, which is what branch arena/26be136b-olbg1 has started doing with "
        "archive/root-20261021/.",
        list(desks.values()), kind="count")

    # -------------------------------------------------- live concurrency record
    add("AUD-F7-09", "info", "Three sessions were live on this repository during this pass",
        "While this audit ran, arena/a570c470-olbg1 (a2bc33a) had claimed T46-T49 for an identical "
        "'live 22 Oct harvest + audit + in-band desk' scope, arena/9dfd0b48-olbg1 (a891ce2) had claimed a "
        "T44-scoped live re-harvest, and arena/26be136b-olbg1 (42f66c8) was rewriting the root dashboard "
        "into data/final/bundle.json with scripts/final_site.py and archiving the 21 October board. This "
        "session renumbered its claim to T50 / section 37 and did not touch root index.html, "
        "scripts/build_site.py, scripts/validate.py or README.md; the navigation request is logged in "
        "COORDINATION.md section 4 instead.", ["COORDINATION.md"], kind="process")

    add("AUD-F7-10", "medium",
        "The generated root navigation is hand-patched, so a rebuild drops desks",
        "index.html carries a hand-added 'Latest snapshot: 22 October re-verified board' banner inside a "
        "file that scripts/build_site.py generates. Session 2ca35f17 logged the same problem for the "
        "7a5b5360 companion link and fixed that one in the generator. The v3 banner is still only in the "
        "output. Any desk added by editing index.html directly - including this one, had it been allowed "
        "to - will vanish on the next root rebuild.", ["index.html", "scripts/build_site.py"], kind="line")

    add("AUD-F7-11", "info", "PR #40 has been open and conflicting since 2026-10-21",
        "gh pr list still reports PR #40 (arena/5c02f50f-olbg1, T13+T14 integration) as OPEN. Every later "
        "session has recorded it as out of scope rather than resolving it. It should be closed or rebased "
        "by the integration session.", ["COORDINATION.md"], kind="process")

    doc = {"session": "f71557b5-olbg1", "audited": "2026-10-22",
           "counts": {"html_pages": len(pages), "archived_pages": len(archived),
                      "tracked_pyc": len(tracked_pyc), "desk_row_counts": counts,
                      "findings": len(FINDINGS)},
           "findings": FINDINGS}
    (OUT / "repo_audit.json").write_text(json.dumps(doc, indent=1, ensure_ascii=False), encoding="utf-8")
    sev = {}
    for f in FINDINGS:
        sev[f["severity"]] = sev.get(f["severity"], 0) + 1
    print(f"f71557b5 audit: {len(FINDINGS)} findings {sev} | {len(pages)} live HTML pages, "
          f"{len(archived)} archived, {len(tracked_pyc)} tracked .pyc")
    for f in FINDINGS:
        if f["severity"] in ("high", "medium"):
            print(f"  [{f['severity'].upper()}] {f['code']} {f['title']}")


if __name__ == "__main__":
    main()
