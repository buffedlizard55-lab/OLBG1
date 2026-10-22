# Session `7f000cb6` — OLBG Reverse-Engineering, Official Audit & Zero-Vig Multi-Market Desk

- **Snapshot UTC**: `2026-10-22T12:30:00Z`
- **Model Version**: `7f000cb6-quant-v1.0`
- **Published Dashboard**: `https://buffedlizard55-lab.github.io/OLBG1/7f000cb6/index.html`
- **Covered Sports**: 17 in-scope sports (`0` rows from excluded soccer, boxing, UFC, MMA, football, American football, hurling, horse racing, cycling, and specials)
- **Audited Entries**: `122` (`40` fully multi-market priced across `280` markets / `560` outcomes; `85` flagged/withheld)
- **High-Confidence Selections**: `9` (100% strictly satisfying `p > 0.7000` AND fair odds in `[-250, +10000]`, 89–95 words each, zero repeated 5-grams/6-grams)

## Key Reverse-Engineering & Repository Audit Highlights
1. **OLBG Split-Timezone Bug**: `Basketball/4`, `Rugby_Union/9`, `Ice_Hockey/13`, `Handball/20`, and `Greyhounds/28` serve unlabeled `BST (UTC+1)` times while `Tennis/3`, `Snooker/8`, `Baseball/12`, `Motor_Racing/14`, `Darts/15`, `Volleyball/21`, and `Gaelic_Football/25` serve unlabeled `EDT (UTC-4)` times. Caught `data/53674ac8/fixtures.json` copying OLBG's `17:45`/`19:45` BST Handball clocks into `start_utc` (+1h error vs official `16:45Z`/`18:45Z`).
2. **OLBG Wrong Fixture Date & Blind Spots**: Caught OLBG `Gaelic_Football/25` listing `Rathgormack v The Nire` (`3536`) on `01 Nov` instead of Munster GAA's official `Sun 25 Oct 2026 14:30`; documented zero-tip blind spots on `Aussie_Rules/22` (AFLW R11), `eSports/23` (LoL Worlds 2026), `Rugby_League/10` (RLWC26 R2), and `Golf/5` (PGA Bermuda Championship).
3. **Official Publisher Prose-vs-Table Contradictions**: Cross-checking `euroleaguebasketball.net` Round 7 Game Center prose against the official 20-club standings table caught two internal publisher errors (`Real Madrid` prose `1-4 away` vs table `2-0 H / 1-3 A`; `Valencia Basket` prose `5-1` vs table `4-2`). Both fixtures are flagged and barred from High confidence.
4. **Line-by-Line Repo Audit (`18` Findings)**: Catalogued in `data/7f000cb6/repo_audit.json` and `/7f000cb6/audit.html` with exact `file:line` pointers.

## Publication & Live Deployment Receipt
- **PR #132**: `https://github.com/buffedlizard55-lab/OLBG1/pull/132` — **MERGED** `2026-10-22T12:45:14Z` (`451eff7888b3a2eb140f9c5d1dee0f4d21102343`).
- **GitHub Actions**: PR check `39780843927` (`success`), `main` canonical Pages publish `39780960162` (`success`), `pages-build-deployment` `39780959657` (`success`).
- **Live URL Verified**: `https://buffedlizard55-lab.github.io/OLBG1/7f000cb6/index.html` (HTTP 200; `/picks.html` and `/flagged.html` also verified live).
