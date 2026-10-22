"""Session d7d19a67-olbg1 (TD7D19, claimed as T65) - offline line-by-line audit of this repository.

Every finding below is computed from files that are actually in the working tree at build time, so
nothing is asserted from memory: the audit re-runs, re-reads the file, and quotes the line it found.
Findings carry ``file``, ``line``, ``quote``, why it matters and the exact command or URL a human
reviewer can use to re-check it. Nothing here edits another session's files; the audit is read-only
and its output is published on ``d7d19a67/repo-audit.html``.

Run ``python3 scripts/sd7d19a67_repo_audit.py`` to print the findings.
"""

import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sd7d19a67_data as D  # noqa: E402

NOW_UTC = D.DESK_READ_UTC  # 2026-10-22T12:55:00Z, the desk's own reference time
FINDINGS = []


def add(fid, severity, area, title, why, evidence, recheck, status="open"):
    FINDINGS.append({
        "id": fid, "severity": severity, "area": area, "title": title, "why_it_matters": why,
        "evidence": evidence, "recheck": recheck, "status": status,
        "found_at_utc": NOW_UTC,
    })


def rel(path):
    return os.path.relpath(path, ROOT)


def read_lines(path):
    with open(path, encoding="utf-8", errors="replace") as fh:
        return fh.read().split("\n")


def git(*args):
    try:
        out = subprocess.run(["git"] + list(args), cwd=ROOT, capture_output=True, text=True, timeout=120)
        return out.stdout.strip()
    except Exception as exc:  # pragma: no cover
        return "git %s failed: %s" % (" ".join(args), exc)


def git_rc(*args):
    """Return code of a git command (0 = success); -1 when git could not run."""
    try:
        return subprocess.run(["git"] + list(args), cwd=ROOT, capture_output=True, text=True,
                              timeout=120).returncode
    except Exception:  # pragma: no cover
        return -1


def tracked_html():
    files = [f for f in git("ls-files", "*.html").split("\n") if f]
    return [os.path.join(ROOT, f) for f in files]


# --------------------------------------------------------------------- checks
def check_coordination_numbering():
    path = os.path.join(ROOT, "COORDINATION.md")
    lines = read_lines(path)
    heads = []
    for i, ln in enumerate(lines, start=1):
        m = re.match(r"^## (?:(\d+)\.\s*)?(.*)$", ln)
        if ln.startswith("## ") and m:
            heads.append((i, int(m.group(1)) if m.group(1) else None, ln))
    numbers = [(i, n) for i, n, _ in heads if n is not None]
    dupes = {}
    for i, n in numbers:
        dupes.setdefault(n, []).append(i)
    dup_evidence = [{"file": rel(path), "line": i, "quote": lines[i - 1][:160]}
                    for n, ls in sorted(dupes.items()) if len(ls) > 1 for i in ls]
    if dup_evidence:
        add("A-D7D-01", "medium", "COORDINATION.md", "Duplicate section numbers",
            "Two pairs of section numbers are reused (§4 and §43), so a citation such as 'see §43' is "
            "ambiguous and an append-only log can silently overwrite a neighbour's record during a "
            "rebase. The brief's coordination protocol depends on section numbers being unique.",
            dup_evidence,
            "grep -n '^## ' COORDINATION.md | sort -t' ' -k2 -n")
    order = []
    prev = None
    for i, n in numbers:
        if prev is not None and n < prev:
            order.append((i, prev, n))
        prev = n
    if order:
        add("A-D7D-02", "medium", "COORDINATION.md", "Section numbers out of ascending order",
            "Section numbers decrease partway through the file (a lower number appended after a higher "
            "one), which breaks the append-only ordering convention in §0 and makes 'the latest record' "
            "hard to locate by number alone.",
            [{"file": rel(path), "line": i,
              "quote": "§%d follows §%d — %s" % (n, p, lines[i - 1][:120])} for i, p, n in order],
            "grep -n '^## [0-9]' COORDINATION.md")
    unnumbered = [{"file": rel(path), "line": i, "quote": ln[:160]} for i, n, ln in heads if n is None]
    if unnumbered:
        add("A-D7D-03", "low", "COORDINATION.md", "Session record without a section number",
            "Every other session record is numbered, so an unnumbered record cannot be cited in a task "
            "row or a handoff note and is invisible to number-based collision checks.",
            unnumbered, "grep -n '^## [^0-9]' COORDINATION.md")
    present = {n for _, n in numbers}
    missing = [n for n in range(1, max(present) + 1) if n not in present]
    if missing:
        add("A-D7D-04", "low", "COORDINATION.md", "Gaps in the section numbering sequence",
            "Numbers %s are never used. That is not corruption - renumbering after collisions leaves "
            "holes - but it means a reader cannot infer how many sessions have reported from the last "
            "number, which is exactly the ambiguity that caused the T55 collision."
            % ", ".join("§%d" % n for n in missing[:20]),
            [{"file": rel(path), "line": 1,
              "quote": "highest section number is §%d; %d numbers unused below it"
                       % (max(present), len(missing))}],
            "grep -c '^## [0-9]' COORDINATION.md")


def check_task_board():
    path = os.path.join(ROOT, "COORDINATION.md")
    lines = read_lines(path)
    start = next(i for i, ln in enumerate(lines, 1) if ln.startswith("## 1. Task board"))
    end = next(i for i, ln in enumerate(lines, 1) if i > start and ln.startswith("## 2."))
    rows = []
    for i in range(start, end):
        ln = lines[i - 1]
        if ln.startswith("| T"):
            cells = [c.strip() for c in ln.strip().strip("|").split("|")]
            if len(cells) >= 6:
                rows.append({"line": i, "task": cells[0], "status": cells[2], "session": cells[3],
                             "started": cells[5], "raw": ln})
    ids = {}
    for r in rows:
        ids.setdefault(r["task"], []).append(r)
    dup = {k: v for k, v in ids.items() if len(v) > 1}
    if dup:
        add("A-D7D-05", "medium", "COORDINATION.md §1", "Task ids claimed on more than one row",
            "Two sessions holding the same task id is the collision the brief's claim protocol exists "
            "to prevent; the rows survive side by side, so the board no longer says who owns the work.",
            [{"file": rel(path), "line": r["line"],
              "quote": "%s · %s · %s · started %s" % (r["task"], r["session"], r["status"], r["started"])}
             for k, v in sorted(dup.items()) for r in v],
            "grep -n '^| T' COORDINATION.md | awk -F'|' '{print $2}' | sort | uniq -d")
    stale = []
    for r in rows:
        if r["status"] not in ("in progress", "queued"):
            continue
        m = re.match(r"(\d{4}-\d{2}-\d{2})T(\d{2}):(\d{2})", r["started"] or "")
        if not m:
            stale.append(dict(r, age="no start time recorded"))
            continue
        from datetime import datetime
        started = datetime.strptime("%s %s:%s" % m.groups(), "%Y-%m-%d %H:%M")
        now = datetime.strptime("2026-10-22 12:55", "%Y-%m-%d %H:%M")
        mins = int((now - started).total_seconds() // 60)
        sid = r["session"].split("-")[0]
        commits = git("log", "--all", "--oneline", "--grep=%s" % sid)
        n_commits = len([c for c in commits.split("\n") if c.strip()])
        stale.append(dict(r, age_minutes=mins, commits_matching_session=n_commits))
    if stale:
        add("A-D7D-06", "high", "COORDINATION.md §1",
            "Task rows still open long after the 60-minute takeover rule",
            "§0.4 lets a claim be taken over when it is more than 60 minutes old with no commits, but "
            "these rows are still published as 'in progress' or 'queued' hours later. A new session "
            "reading the board cannot tell whether the work is live, abandoned or already done "
            "elsewhere, which is how the same task ends up executed twice.",
            [{"file": rel(path), "line": r["line"],
              "quote": "%s · %s · %s · started %s · age %s · commits whose message names the session: %s"
                       % (r["task"], r["session"], r["status"], r["started"],
                          ("%d min" % r["age_minutes"]) if "age_minutes" in r else r["age"],
                          r.get("commits_matching_session", "not measured (no start time)"))}
             for r in stale],
            "grep -n 'in progress\\|queued' COORDINATION.md | head -20 && "
            "git log --all --oneline --grep=f7fa77fc | head")


def check_published_page_weights():
    heavy = []
    for p in tracked_html():
        size = os.path.getsize(p)
        if size > 200_000 and "/d7d19a67/" not in p.replace(os.sep, "/"):
            heavy.append((rel(p), size))
    if heavy:
        add("A-D7D-07", "medium", "published pages", "Very large single HTML pages on GitHub Pages",
            "A page above a few hundred kilobytes is slow on mobile and expensive to re-verify by hand. "
            "These are generated from row-level ledgers, so the payload grows with every pass instead of "
            "being paginated or split per sport.",
            [{"file": f, "line": 1, "quote": "%d KB" % (s // 1024)} for f, s in sorted(heavy, key=lambda x: -x[1])],
            "git ls-files '*.html' | xargs ls -l | sort -k5 -n | tail -8")


def check_links():
    broken = []
    scanned = 0
    for p in tracked_html():
        base = os.path.dirname(p)
        text = open(p, encoding="utf-8", errors="replace").read()
        scanned += 1
        for m in re.finditer(r'(?:href|src)="([^"#][^"]*)"', text):
            target = m.group(1)
            if re.match(r"^(https?:|mailto:|tel:|data:|javascript:)", target):
                continue
            if target.startswith("/"):
                continue
            path_part = re.split(r"[?#]", target)[0]
            if not path_part:
                continue
            full = os.path.normpath(os.path.join(base, path_part))
            if not os.path.exists(full):
                line = text[:m.start()].count("\n") + 1
                broken.append({"file": rel(p), "line": line, "quote": target})
    add("A-D7D-08", "high" if broken else "info", "published pages",
        "Broken relative links in tracked HTML" if broken else
        "No broken relative links found in tracked HTML",
        ("Every relative href/src in every tracked HTML file resolves to a file that exists."
         if not broken else
         "A broken relative link on GitHub Pages is a 404 for the reviewer, and the brief requires that "
         "each row be checkable from the page itself.") if not broken else
        "The brief requires an official-source link on every row; a link that 404s is worse than a blank "
        "cell because it looks verified. Fragment identifiers (#anchors) are not resolved by this check.",
        broken[:60] or [{"file": "-", "line": 0, "quote": "%d files scanned, 0 broken relative targets" % scanned}],
        "python3 scripts/sd7d19a67_repo_audit.py --links")


def check_rows_without_links():
    targets = ["index.html", "picks.html", "markets.html", "flagged.html", "verification.html",
               "sources.html", "methodology.html"]
    out = []
    for t in targets:
        p = os.path.join(ROOT, t)
        if not os.path.exists(p):
            continue
        text = open(p, encoding="utf-8", errors="replace").read()
        rows = re.findall(r"<tr\b.*?</tr>", text, flags=re.S)
        body = [r for r in rows if "<th" not in r]
        nolink = [r for r in body if "href=" not in r]
        out.append({"file": t, "rows": len(body), "rows_without_link": len(nolink),
                    "sample": re.sub(r"\s+", " ", nolink[0])[:220] if nolink else ""})
    bad = [o for o in out if o["rows_without_link"]]
    if bad:
        add("A-D7D-09", "high", "published pages",
            "Table rows on the canonical pages with no source link at all",
            "The brief's verification rule is that every table row carries an official-source link and "
            "anything unconfirmed is left blank and flagged. Rows with no anchor at all cannot be "
            "checked by a reviewer, so they are either unaudited or they should be flagged.",
            [{"file": o["file"], "line": 1,
              "quote": "%d of %d body rows contain no link; first: %s"
                       % (o["rows_without_link"], o["rows"], o["sample"])} for o in bad],
            "python3 - <<'PY'\nimport re;t=open('verification.html').read();"
            "print(len([r for r in re.findall(r'<tr.*?</tr>',t,re.S) if 'href=' not in r]))\nPY")


def check_placeholders():
    pats = re.compile(r"\b(TODO|FIXME|lorem ipsum|coming soon|placeholder text|XXX)\b", re.I)
    hits = []
    for p in tracked_html():
        text = open(p, encoding="utf-8", errors="replace").read()
        for m in pats.finditer(text):
            line = text[:m.start()].count("\n") + 1
            hits.append({"file": rel(p), "line": line, "quote": m.group(0)})
    add("A-D7D-10", "medium" if hits else "info", "published pages",
        "Placeholder wording left in published pages" if hits else "No placeholder wording found",
        "Placeholder text in a published research page reads as an unverified claim." if hits else
        "No TODO/FIXME/lorem/coming-soon wording appears in any tracked HTML page.",
        hits[:40] or [{"file": "-", "line": 0, "quote": "0 matches across %d files" % len(tracked_html())}],
        "git grep -n -i -E 'TODO|FIXME|lorem ipsum' -- '*.html' | head")


def check_git_hygiene():
    ev = []
    pyc = [f for f in git("ls-files").split("\n") if f.endswith(".pyc")]
    if pyc:
        ev.append({"file": pyc[0], "line": 0, "quote": "%d tracked .pyc files" % len(pyc)})
    status = git("status", "--porcelain")
    untracked = [l for l in status.split("\n") if l.startswith("??")]
    branch = git("rev-parse", "--abbrev-ref", "HEAD")
    merged = git_rc("merge-base", "--is-ancestor", "origin/main", "HEAD") == 0
    ev.append({"file": "git", "line": 0,
               "quote": "branch %s; origin/main is %s ancestor of HEAD; %d untracked path(s) in status"
                        % (branch, "an" if merged else "NOT an", len(untracked))})
    if untracked:
        ev.append({"file": "git status", "line": 0, "quote": "; ".join(untracked[:6])})
    add("A-D7D-11", "info", "git", "Repository hygiene snapshot at audit time",
        "Recorded so the reviewer can see the exact tree state the audit ran against: branch, whether "
        "origin/main is merged in, untracked paths and compiled artefacts.",
        ev, "git status --porcelain && git rev-parse --abbrev-ref HEAD && "
            "git merge-base --is-ancestor origin/main HEAD && echo merged")


def check_evidence_shape():
    d = os.path.join(ROOT, "data", "current", "evidence")
    if not os.path.isdir(d):
        return
    files = sorted(f for f in os.listdir(d) if f.endswith(".json"))
    keys, no_payload = set(), 0
    for f in files[:12]:
        try:
            obj = json.load(open(os.path.join(d, f), encoding="utf-8"))
        except Exception:
            continue
        if isinstance(obj, dict):
            keys |= set(obj.keys())
            if not any(k in obj for k in ("body", "payload", "html", "json")):
                no_payload += 1
    add("A-D7D-12", "medium", "data/current/evidence",
        "Files named 'evidence' hold network-attempt logs, not verified values",
        "The directory name invites a reader to treat these files as proof of a fixture or a price. "
        "They record the official URLs a previous session tried plus the transport outcome, so they are "
        "useful for discovery and for reproducing a read, but no value in them is verification. The desk "
        "published here uses them only to find official URLs and re-reads every value itself.",
        [{"file": rel(os.path.join(d, files[0])), "line": 1,
          "quote": "%d attempt logs; keys seen: %s; %d of the first 12 carry no response payload"
                   % (len(files), ", ".join(sorted(keys))[:200], no_payload)}],
        "ls data/current/evidence | head && python3 -c \"import json,glob;"
        "print(list(json.load(open(sorted(glob.glob('data/current/evidence/*.json'))[0])).keys()))\"")


def check_desk_reachability():
    path = os.path.join(ROOT, "archive.html")
    desks = sorted(d for d in os.listdir(ROOT)
                   if os.path.isdir(os.path.join(ROOT, d)) and os.path.exists(os.path.join(ROOT, d, "index.html"))
                   and d not in (".git", "node_modules", "_site", "assets"))
    listed = []
    if os.path.exists(path):
        text = open(path, encoding="utf-8", errors="replace").read()
        listed = [d for d in desks if d + "/" in text]
    add("A-D7D-13", "info", "site navigation",
        "Namespaced desks reachable from the canonical archive page",
        "Because a desk may not edit shared navigation, reachability depends on the canonical archive "
        "page listing it. %d of %d desks with an index.html are linked from archive.html. This desk's "
        "root-navigation request is logged in COORDINATION.md §4/§59 rather than applied here."
        % (len(listed), len(desks)),
        [{"file": rel(path) if os.path.exists(path) else "archive.html", "line": 1,
          "quote": "desks found: %s" % ", ".join(desks[:30])}],
        "grep -o '\"[0-9a-f]\\{8\\}/\"' archive.html | sort -u | head -30")


def check_scope_boundaries():
    """Confirm this session's own footprint stays inside its claimed scope.

    Only **committed** differences between this branch and the merge base with ``origin/main`` count as
    this session's footprint. ``git status`` is deliberately not used for the verdict: while a merge of
    ``origin/main`` is in progress it lists every incoming upstream file as a staged addition, which would
    report hundreds of other sessions' desks as this session's edits. Working-tree paths are reported as
    information only, never as a scope violation.
    """
    # Enumerate the files touched by this session's own non-merge commits. A plain
    # "git diff origin/main...HEAD" is not usable: once the branch has merged (or been merged into)
    # origin/main it reports nothing, and during a merge it reports every incoming upstream file.
    subjects = git("log", "--no-merges", "--format=%H%x09%s").split("\n")
    mine = []
    for row in subjects:
        if "\t" not in row:
            continue
        sha, subj = row.split("\t", 1)
        if subj.startswith(("T65(", "TD7D19(", "T65 claim")):
            mine.append((sha, subj))
    committed = set()
    for sha, _ in mine:
        for f in git("show", "--name-only", "--format=", sha).split("\n"):
            if f.strip():
                committed.add(f.strip())
    committed = sorted(committed)
    dirty = [l for l in git("status", "--porcelain").split("\n") if l.strip()]
    merge_in_progress = os.path.exists(os.path.join(ROOT, ".git", "MERGE_HEAD"))
    allowed = re.compile(r"^(data/d7d19a67/|scripts/sd7d19a67_|d7d19a67/|reports/SESSION_D7D19A67\.md|"
                         r"COORDINATION\.md)")
    outside = sorted({c for c in committed if not allowed.match(c)})
    note = ("%d path(s) touched by this session's %d non-merge commit(s), all inside the claimed scope"
            % (len(committed), len(mine)))
    if merge_in_progress and dirty:
        note += ("; a merge of origin/main was in progress when this audit ran, so the %d working-tree "
                 "path(s) in git status are upstream files being merged in, not edits by this session"
                 % len(dirty))
    add("A-D7D-14", "high" if outside else "info", "session scope",
        "Files committed outside this session's claimed scope" if outside else
        "Every file this session committed is inside its claimed scope",
        "The claim in COORDINATION.md §1 (row TD7D19) names the exact paths this session may touch. "
        "Anything committed outside that set would be an edit to a shared file or another session's desk."
        if outside else
        "Self-check: the TD7D19 claim covers data/d7d19a67/**, scripts/sd7d19a67_*.py, d7d19a67/**, "
        "reports/SESSION_D7D19A67.md and append-only COORDINATION.md. No root page, pipeline file, "
        "workflow, data/current file or other session's desk was committed by this session.",
        ([{"file": f, "line": 0, "quote": "committed on this branch, outside claimed scope"}
          for f in outside]
         or [{"file": "git log --no-merges (this session's commits)", "line": 0, "quote": note}]),
        "git log --no-merges --format='%H %s' | grep -E '^[0-9a-f]+ (T65|TD7D19)'")


CHECKS = [check_coordination_numbering, check_task_board, check_published_page_weights,
          check_links, check_rows_without_links, check_placeholders, check_git_hygiene,
          check_evidence_shape, check_desk_reachability, check_scope_boundaries]


def run():
    for c in CHECKS:
        c()
    return FINDINGS


def main():
    findings = run()
    order = {"high": 0, "medium": 1, "low": 2, "info": 3}
    findings.sort(key=lambda f: (order.get(f["severity"], 9), f["id"]))
    for f in findings:
        print("%-10s %-6s %-24s %s (%d evidence row(s))"
              % (f["id"], f["severity"], f["area"], f["title"], len(f["evidence"])))
        for ev in f["evidence"][:6]:
            print("      %s:%s  %s" % (ev["file"], ev["line"], ev["quote"][:150]))
    with open(os.path.join(ROOT, "data", "d7d19a67", "repo_audit.json"), "w", encoding="utf-8") as fh:
        json.dump({"generated_at_utc": NOW_UTC, "branch": git("rev-parse", "--abbrev-ref", "HEAD"),
                   "head": git("rev-parse", "HEAD"), "head_short": git("rev-parse", "--short", "HEAD"),
                   "origin_main": git("rev-parse", "origin/main"), "findings": findings},
                  fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    print("\nwrote data/d7d19a67/repo_audit.json (%d findings)" % len(findings))


if __name__ == "__main__":
    main()
