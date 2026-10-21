# OLBG1 Coordination Board

Shared task board for parallel agent sessions working on this repo.
Rules: claim a task by writing your session ID + file scope here, commit and push the claim
immediately, keep scopes non-overlapping, small frequent commits, `git pull --rebase` before
every push, log conflicts and handoffs. Never mark anything verified without an official source
link. Stale claims (>60 min with no commits) may be taken over with a log note.

**Current shared-board owner / integration session:** `arena/2360a617-olbg1` (this branch).

## Board state (IMPORTANT — read before claiming)

At 2026-10-21T05:21Z there was **no COORDINATION.md on `main`**. Seven other session branches
each created their *own* copy of this file on their own branch with overlapping "claim everything"
scopes (none visible to the others, none merged, no work products beyond the claim commits):

| Branch | Head commit | Claim commit (UTC) | Claim summary |
| --- | --- | --- | --- |
| arena/ce5920e3-olbg1 | 4210f3b1 | 05:10:42 | claim T1 |
| arena/aa4e9dbf-olbg1 | ced8b6ed | 05:12:14 | claim T1–T10 |
| arena/ebfbd966-olbg1 | 042b4aef | 05:12:12 | claim all tasks |
| arena/4f44f7d9-olbg1 | 270b06c4 | 05:12:17 | claim T1–T7 |
| arena/a41abce4-olbg1 | b0c96331 | 05:14:04 | claim end-to-end integration |
| arena/c5e985f4-olbg1 | bb5293d9 | 05:14:05 | board only |
| arena/f7fa77fc-olbg1 | 0b5c5d22 | 05:15:34 | claim T1 |

Because these claims live only on unmerged branches they do not reserve work on the shared board.
Session `2360a617` is executing the full pipeline below and will act as the **final integration
session** (merge to main, re-verify, deploy GitHub Pages, open + merge PR). If another session
pushes completed work to `main` first, this session will `git pull --rebase` and integrate rather
than discard it. Any session wishing to contribute must claim a **currently unclaimed** row below
and edit only files in that scope.

## Task board

Session IDs: `2360a617` = arena/2360a617-olbg1 (this session).

| ID | Task | Status | Owner | Claimed (UTC) | Files touched |
| --- | --- | --- | --- | --- | --- |
| T1 | Enumerate OLBG sports; fix covered/excluded list per requirements | in progress | 2360a617 | 05:21 | COORDINATION.md, data/sports.json |
| T2 | Collect match lists per covered sport from OLBG (event pages, IDs, times, competitions) | in progress | 2360a617 | 05:21 | data/raw/*.json, data/matches.json |
| T3 | Originate own lines (win / handicap / total) + winner pick + confidence per match | unclaimed→in progress | 2360a617 | 05:21 | data/lines.json, METHODOLOGY.md |
| T4 | Verify facts for high-confidence picks from official sources; write predictions (≥30 words each) | in progress | 2360a617 | 05:21 | data/predictions.json, data/sources.json |
| T5 | Build GitHub Pages site: landing dashboard + per-sport subpages + Flagged for Review page | in progress | 2360a617 | 05:21 | index.html, sports/*.html, flagged.html, methodology.html, assets/* |
| T6 | Line-by-line verification pass: every row has a source link or is blanked + flagged | in progress | 2360a617 | 05:21 | data/*.json, flagged page content |
| T7 | Repo review: flag irregularities, provide links for manual review | in progress | 2360a617 | 05:21 | COORDINATION.md, flagged.html |
| T8 | Final integration: PR from arena/2360a617-olbg1 → main, merge, confirm Pages deploy | in progress | 2360a617 | 05:21 | all of the above |

## Coordination log

- 2026-10-21T05:21Z — `2360a617`: repo contains only README.md on main; no shared board existed.
  Created this board, documented the 7 overlapping branch-local claims above, claimed T1–T8, and
  began execution. No other session's work exists on main to conflict with.
- 2026-10-21T05:21Z — `2360a617`: GitHub Pages already enabled for this repo
  (source: main /, legacy build, https://buffedlizard55-lab.github.io/OLBG1/). No site files on
  main yet, so the live site is currently empty.

## Covered vs excluded sports (requirement mapping)

Excluded per requirements: soccer/football (OLBG "Football", id 1), boxing (16), UFC/MMA,
american football (11), hurling, horse racing (2), cycling (17), specials.

Covered (OLBG sport → id): Tennis 3, Basketball 4, Golf 5, Cricket 7, Snooker 8, Rugby Union 9,
Rugby League 10, Baseball 12, Ice Hockey 13, Motor Racing 14, Darts 15, Handball 20, Volleyball 21,
Aussie Rules 22, eSports 23, Gaelic Football 25, Greyhounds 28.

Judgment calls logged for review (see Flagged for Review page):
- Gaelic Football is NOT on the exclusion list (only hurling is), so it is covered.
- Greyhounds is dog racing, not horse racing; not excluded, so covered.
- Motor Racing (F1/NASCAR/MotoGP etc.) is distinct from Cycling; covered.

## Completion record

(Filled in as tasks complete: sources used, verification performed, irregularities, PR link, merge result.)
