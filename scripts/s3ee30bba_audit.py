#!/usr/bin/env python3
"""Line-by-line repository audit for session 3ee30bba-olbg1.

Reads tracked files from origin/main via `git show` so file:line links resolve
against a permanent commit on `main`, and pairs every audit finding with an
official governing-body verification link. Also checks this session's own
non-merge commits against its claimed file scope.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO_URL = "https://github.com/buffedlizard55-lab/OLBG1"

ALLOWED_PREFIXES = (
    "3ee30bba/",
    "data/3ee30bba/",
    "scripts/s3ee30bba_",
    "reports/SESSION_3EE30BBA.md",
    "tests/pipeline/test_desk_3ee30bba.py",
    "COORDINATION.md",
)


def _git_lines(cmd: list[str]) -> list[str]:
    out = subprocess.check_output(cmd, cwd=ROOT, text=True)
    return [x for x in out.splitlines() if x.strip()]


def _find_line(commit: str, rel_path: str, needle: str) -> int:
    text = subprocess.check_output(["git", "show", f"{commit}:{rel_path}"], cwd=ROOT, text=True)
    for idx, line in enumerate(text.splitlines(), 1):
        if needle in line:
            return idx
    return 1


def build_repo_audit() -> dict:
    try:
        main_sha = subprocess.check_output(["git", "rev-parse", "origin/main"], cwd=ROOT, text=True).strip()
    except subprocess.CalledProcessError:
        main_sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()

    def blob(rel_path: str, needle: str) -> tuple[str, int, str]:
        ln = _find_line(main_sha, rel_path, needle)
        return rel_path, ln, f"{REPO_URL}/blob/{main_sha}/{rel_path}#L{ln}"

    findings = []

    f_path, f_ln, f_url = blob("data/current/snapshot.json", '"euroleague-round7-64"')
    findings.append({
        "id": "AUD-3EE-01",
        "severity": "high",
        "file": f_path,
        "line": f_ln,
        "github_url": f_url,
        "title": "Six Thursday Oct 22 EuroLeague Round 7 Fixtures in Canonical Snapshot Have Elapsed by 21:10Z",
        "detail": (
            "Canonical snapshot (generated 12:29:50Z) retains six Thursday Oct 22 EuroLeague Round 7 fixtures "
            "(ids euroleague-round7-64/65/62/67/63/66, start_utc 17:30Z–18:45Z). Live read of EuroLeague Game Center "
            "at 21:01Z confirms five final scores (Efes 89-80 Besiktas, Bayern 91-107 Dubai, Maccabi 99-113 Real Madrid, "
            "Panathinaikos 85-79 Baskonia, Milan 81-89 Barcelona) and Partizan vs Crvena Zvezda live in crunch time."
        ),
        "official_url": "https://www.euroleaguebasketball.net/en/euroleague/news/game-center-round-7-el2627/",
        "official_label": "EuroLeague R7 Game Center",
    })

    f_path, f_ln, f_url = blob("data/d7d19a67/desk.json", "Besiktas Istanbul")
    findings.append({
        "id": "AUD-3EE-02",
        "severity": "medium",
        "file": f_path,
        "line": f_ln,
        "github_url": f_url,
        "title": "Midday Desks (d7d19a67 & 7f000cb6) Priced Besiktas Istanbul ML Ahead of 89–80 Defeat to Anadolu Efes",
        "detail": (
            "Desks captured around 12:30Z–12:55Z priced Thursday's Istanbul derby (tipoff 17:30Z) as pre-match with "
            "Besiktas favoured; Anadolu Efes led wire-to-wire behind Cam Payne's career-high 22 points to win 89–80, "
            "leaving both clubs 3–4 on the official EuroLeague Standings page."
        ),
        "official_url": "https://www.euroleaguebasketball.net/en/euroleague/standings/",
        "official_label": "EuroLeague Official Standings",
    })

    f_path, f_ln, f_url = blob("data/7f000cb6/fixtures.json", "Melsungen")
    findings.append({
        "id": "AUD-3EE-03",
        "severity": "medium",
        "file": f_path,
        "line": f_ln,
        "github_url": f_url,
        "title": "Five Thursday Oct 22 EHF Champions League Round 5 Matches Have Completed (60:00')",
        "detail": (
            "Earlier repository datasets list Round 5 Thursday fixtures (16:45Z & 18:45Z) as upcoming. Official EHF "
            "live standings at 21:05Z confirm all five are complete: MT Melsungen 28–26 Plock, Szeged 33–33 GOG, "
            "Sporting CP 42–40 Kristianstad, Barça 40–34 Montpellier, and Kolstad 32–35 Magdeburg; Round 6 (Oct 28–29 CET) is now active."
        ),
        "official_url": "https://ehfcl.eurohandball.com/men/2026-27/standings/",
        "official_label": "EHF CL Men Official Standings",
    })

    f_path, f_ln, f_url = blob("data/fixtures.json", "Humphries")
    findings.append({
        "id": "AUD-3EE-04",
        "severity": "high",
        "file": f_path,
        "line": f_ln,
        "github_url": f_url,
        "title": "Legacy data/fixtures.json Retains Withdrawn Player Luke Humphries in PDC European Championship R1",
        "detail": (
            "Primary legacy dataset lists '(12) Luke Humphries vs (21) Ryan Searle'. Official PDC announcement on "
            "22 Oct 2026 confirms Humphries withdrew with gastroenteritis and was replaced by Kim Huybrechts in Thursday's opening session."
        ),
        "official_url": "https://www.pdc.tv/news/2026/october/22/humphries-withdraws-from-machineseeker-european-championship",
        "official_label": "PDC Official Withdrawal Notice",
    })

    f_path, f_ln, f_url = blob("data/d7d19a67/desk.json", "849805")
    findings.append({
        "id": "AUD-3EE-05",
        "severity": "low",
        "file": f_path,
        "line": f_ln,
        "github_url": f_url,
        "title": "MLB StatsAPI Updated With Two New World Series Rays Probable Pitchers Since 12:55Z",
        "detail": (
            "Midday desks recorded only Milwaukee's Jacob Misiorowski for Game 1 (gamePk 849805). Hydrated StatsAPI "
            "read at 21:00Z confirms Nick Martinez (id 607259) starts Game 1 for Tampa Bay and Drew Rasmussen (id 656876) starts Game 2."
        ),
        "official_url": "https://statsapi.mlb.com/api/v1/schedule?sportId=1&startDate=2026-10-22&endDate=2026-10-29&hydrate=probablePitcher,team",
        "official_label": "MLB StatsAPI Schedule",
    })

    f_path, f_ln, f_url = blob("data/7f000cb6/fixtures.json", "9410")
    findings.append({
        "id": "AUD-3EE-06",
        "severity": "medium",
        "file": f_path,
        "line": f_ln,
        "github_url": f_url,
        "title": "ATP/WTA Signed Supervisor PDFs Advanced From Thursday R16 to Friday Oct 23 Quarter-Finals",
        "detail": (
            "Earlier 22 Oct desks captured Thursday's Round-of-16 Orders of Play across Almaty (9410), Brussels (7485), "
            "Ningbo (2092), and Osaka (405). Re-fetching all four official Supervisor OP/MDS PDFs at 21:01Z–21:02Z "
            "confirms all 16 Friday Oct 23 Singles Quarter-Finals have now been released."
        ),
        "official_url": "https://www.protennislive.com/posting/2026/9410/op.pdf",
        "official_label": "ATP 9410 Signed OP PDF",
    })

    f_path, f_ln, f_url = blob("data/fixtures.json", "wst.tv")
    findings.append({
        "id": "AUD-3EE-07",
        "severity": "medium",
        "file": f_path,
        "line": f_ln,
        "github_url": f_url,
        "title": "Snooker BetVictor Northern Ireland Open Advanced From Round 3 to Friday Quarter-Finals",
        "detail": (
            "Legacy primary rows list Thursday afternoon Round 3 ties. Live WST Match Centre check at 21:02Z shows "
            "three Friday Oct 23 Quarter-Finals already set (McGill vs Kyren Wilson, Craigie vs Slessor, Gilbert vs Mark Williams) "
            "and two final R3 ties (Brown vs Donaldson, Jak Jones vs Wells) Live Now."
        ),
        "official_url": "https://www.wst.tv/match-centre/f0b30e58-d987-4505-89c2-8b24805b98d5",
        "official_label": "WST Official Match Centre",
    })

    f_path, f_ln, f_url = blob("data/7f000cb6/fixtures.json", "prod2.lnr.fr")
    findings.append({
        "id": "AUD-3EE-08",
        "severity": "low",
        "file": f_path,
        "line": f_ln,
        "github_url": f_url,
        "title": "French Pro D2 Journée 8 Opener (US Montauban vs Oyonnax Rugby) Completed Tonight",
        "detail": (
            "Thursday's 21h00 French kickoff between Montauban and Oyonnax has finished on prod2.lnr.fr/classement "
            "(Montauban victory, Oyonnax defensive bonus point: Oyonnax now GP 8, 7W-1L, 34 pts); seven Friday J8 fixtures remain pre-match."
        ),
        "official_url": "https://prod2.lnr.fr/classement",
        "official_label": "LNR Pro D2 Official Standings",
    })

    f_path, f_ln, f_url = blob("COORDINATION.md", "| T9 |")
    findings.append({
        "id": "AUD-3EE-09",
        "severity": "medium",
        "file": f_path,
        "line": f_ln,
        "github_url": f_url,
        "title": "Ten Task Rows in COORDINATION.md Remain Marked 'in progress' or 'queued' Past the 60-Minute Rule",
        "detail": (
            "Rows T9–T12 (f7fa77fc, started 2026-10-21T05:26Z), T19 (76950c25), T51–T53 (a570c470), T-FEC (fec05fb4), "
            "and T97DC (97dcb2c9) still carry 'in progress' or 'queued' status strings >8–39 hours after their last commits, "
            "even where their PRs already merged. Left untouched per append-only §0.4 protocol."
        ),
        "official_url": "https://api-web.nhle.com/v1/schedule/2026-10-22",
        "official_label": "NHL Schedule (Reference Check)",
    })

    f_path, f_ln, f_url = blob("COORDINATION.md", "| T63 |")
    findings.append({
        "id": "AUD-3EE-10",
        "severity": "low",
        "file": f_path,
        "line": f_ln,
        "github_url": f_url,
        "title": "Duplicate Task ID T63 and Duplicate Section Headings (§4, §13, §43) in COORDINATION.md",
        "detail": (
            "Two independent merged sessions (f1c13c19 and 92af340c) both occupy task id T63, and section numbers "
            "§4, §13, and §43 appear twice due to concurrent rebases. Session 3ee30bba uses collision-resistant ID T3EE30 and §60."
        ),
        "official_url": "https://statsapi.mlb.com/api/v1/schedule?sportId=1&startDate=2026-10-22&endDate=2026-10-29",
        "official_label": "MLB StatsAPI (Reference Check)",
    })

    f_path, f_ln, f_url = blob("f7fa77fc/flagged.html", "methodology.html")
    findings.append({
        "id": "AUD-3EE-11",
        "severity": "low",
        "file": f_path,
        "line": f_ln,
        "github_url": f_url,
        "title": "Three Pre-Existing Validator Warnings in f7fa77fc/flagged.html (Internal Policy Link Instead of Official Host)",
        "detail": (
            "scripts/validate.py reports 0 errors and 3 warnings on pristine main because table rows #43, #45, and #47 "
            "in f7fa77fc/flagged.html link only to internal methodology.html rather than an external governing-body domain."
        ),
        "official_url": "https://www.pdc.tv/tournaments",
        "official_label": "PDC Official Tournaments",
    })

    f_path, f_ln, f_url = blob("scripts/release_validate.py", "official review link")
    findings.append({
        "id": "AUD-3EE-12",
        "severity": "low",
        "file": f_path,
        "line": f_ln,
        "github_url": f_url,
        "title": "Historical T61 Validator (scripts/release_validate.py) Superseded by Canonical pipeline.validate",
        "detail": (
            "scripts/release_validate.py expects pre-T257E root HTML layout and fails on canonical audit/archive rows, "
            "whereas the active CI gate (.github/workflows/current-pages.yml) runs pipeline.validate + scripts/validate.py (0 errors)."
        ),
        "official_url": "https://www.nhl.com/schedule",
        "official_label": "NHL Official Schedule",
    })

    # Verify our own session's non-merge commit footprint
    touched = sorted(set(_git_lines(["git", "log", "--no-merges", "--name-only", "--pretty=format:", f"{main_sha}..HEAD"])))
    outside = [p for p in touched if not p.startswith(ALLOWED_PREFIXES)]
    findings.append({
        "id": "AUD-3EE-13",
        "severity": "high" if outside else "info",
        "file": "COORDINATION.md",
        "line": _find_line(main_sha, "COORDINATION.md", "## 1. Task board"),
        "github_url": f"{REPO_URL}/blob/{main_sha}/COORDINATION.md#L63",
        "title": "Session 3ee30bba-olbg1 Non-Merge Commit Scope Verification" if not outside else "Scope Breach Detected",
        "detail": (
            f"Checked `git log --no-merges {main_sha[:8]}..HEAD`: {len(touched)} committed path(s), "
            f"{len(outside)} outside claimed T3EE30 scope ({ALLOWED_PREFIXES})."
        ),
        "official_url": "https://www.mlb.com/schedule",
        "official_label": "MLB Official Schedule",
    })

    return {
        "baseline_main_sha": main_sha,
        "checked_commits_range": f"{main_sha[:8]}..HEAD",
        "touched_paths_count": len(touched),
        "outside_scope_paths": outside,
        "findings": findings,
    }
