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
| T-02 | Data collection: match list for allowed sports (all sports EXCEPT soccer, boxing, UFC/MMA, football, American football, hurling, horse racing, cycling, specials) | done | arena-c5e985f4-olbg1 | data/matches.json | web_search + official club/federation sites | 72 entries across 13 sports (tennis, NBA, MLB, cricket, rugby union URC, NHL, golf, snooker, darts, badminton, table tennis, volleyball, handball). Sources linked per row. OLBG.com unreachable from sandbox; lines originated by this session, not copied from bookmakers. |
| T-03 | Originate betting lines; pick match winner; confidence low/medium/high; investigate markets (win match, handicap, match total, etc.) | done | arena-c5e985f4-olbg1 | data/matches.json | originated lines (American odds); no bookmaker odds copied | All rows have moneyline pick + odds + handicap + total where applicable; outright markets for tournaments marked n/a/low |
| T-04 | High-confidence predictions: unique, human, 30+ words, verified info from official sources (team, player, form, recent history, clear betting selection) | done | arena-c5e985f4-olbg1 | data/matches.json | MLB.com, ESPN, BBC, unitedrugby.com | 6 high-confidence picks written: Brewers WS G1, Nets@Cavs, Pelicans@Nuggets, Lakers@Thunder, Bulls@Celtics, Leinster v Munster (all 30+ words with clear selection) |
| T-05 | Line-by-line verification; every table row has a source link; blank + flagged if unverified | done | arena-c5e985f4-olbg1 | data/matches.json | per-row sources in JSON | All 72 rows have source links; partial/unverified flags where unconfirmed (tennis matchups, WS G5-G7, URC venues, volleyball venues) |
| T-06 | Site build: GitHub Pages site, clean landing page, category subpages, dashboard tables, analysis/findings | done | arena-c5e985f4-olbg1 | *.html (root) | n/a | 17 pages: index + 13 sport pages + methodology + findings + flagged; generated from data/matches.json |
| T-07 | Flagged for Review page (unverified items + source links) | done | arena-c5e985f4-olbg1 | flagged.html | n/a | 12 flagged rows listed with issues and source links |
| T-08 | Final integration: verify build, no broken links, publish GitHub Pages, PR to main, merge, record result | in progress | arena-c5e985f4-olbg1 | all | n/a | Build verified (17 pages, no broken internal links); PR + Pages deploy pending |

## Session claims
- arena-c5e985f4-olbg1: T-01..T-07 done, T-08 in progress

## Log
- 2026-10-21: Repo is empty apart from README.md. COORDINATION.md created. OLBG.com not directly reachable (TLS blocked); match data must come via web_search + official sources.
