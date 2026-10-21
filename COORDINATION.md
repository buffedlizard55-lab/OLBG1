# OLBG — Coordination Board

Session branch: `arena/c5e985f4-olbg1` (session id: `arena-c5e985f4-olbg1`)
Repo: https://github.com/buffedlizard55-lab/OLBG1

## Ground rules
- Claim a task by writing your session id + file scope here, commit + push immediately.
- Never start a task another session has claimed. Keep scopes non-overlapping.
- Work line by line; verify every value against an official/trusted source; link the source.
- Unverifiable values: leave blank, flag "unverified", list on "Flagged for Review" page.
- Small, frequent commits. `git pull --rebase` before every push. Resolve conflicts without discarding others' work.
- Claim older than 60 minutes with no commits may be taken over (note the handoff in the log).
- Final integration session: merges branches, re-verifies line by line, confirms site builds with no broken links, publishes to GitHub Pages, opens + merges PR to main, records PR link + result here.

## Task list

| ID | Task | Status | Owner | Files touched | Sources / verification | Notes |
|----|------|--------|-------|---------------|------------------------|-------|
| T-01 | COORDINATION.md setup (shared task board) | done | arena-c5e985f4-olbg1 | COORDINATION.md | n/a | Initial claim |
| T-02 | Data collection: match list for allowed sports (all sports EXCEPT soccer, boxing, UFC/MMA, football, American football, hurling, horse racing, cycling, specials) | unclaimed | — | data/*.json | web_search + official club/federation sites | OLBG.com not reachable from sandbox; using web_search |
| T-03 | Originate betting lines; pick match winner; confidence low/medium/high; investigate markets (win match, handicap, match total, etc.) | unclaimed | — | data/*.json | reasoning + official stats | no hallucinations |
| T-04 | High-confidence predictions: unique, human, 30+ words, verified info from official sources (team, player, form, recent history, clear betting selection) | unclaimed | — | data/*.json, site pages | official club/federation sources | |
| T-05 | Line-by-line verification; every table row has a source link; blank + flagged if unverified | unclaimed | — | data/*.json | official sources | |
| T-06 | Site build: GitHub Pages site, clean landing page, category subpages, dashboard tables, analysis/findings | unclaimed | — | site/*.html | n/a | |
| T-07 | Flagged for Review page (unverified items + source links) | unclaimed | — | site/flagged.html | n/a | |
| T-08 | Final integration: verify build, no broken links, publish GitHub Pages, PR to main, merge, record result | unclaimed | — | all | n/a | Blocks nothing until done |

## Session claims
- arena-c5e985f4-olbg1: T-01 (done), T-02 (in progress), T-03 (planned), T-04 (planned), T-05 (planned), T-06 (planned), T-07 (planned), T-08 (planned)

## Log
- 2026-10-21: Repo is empty apart from README.md. COORDINATION.md created. OLBG.com not directly reachable (TLS blocked); match data must come via web_search + official sources.
