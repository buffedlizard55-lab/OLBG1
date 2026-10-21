# OLBG1 — OLBG match board with originated lines & picks

Independent research project: a dated snapshot (2026-10-21) of OLBG.com tip
listings for every covered sport — **excluding** soccer/football, boxing/UFC/MMA,
American football, hurling, horse racing, cycling and specials — with our own
originated fair prices, a winner pick and a Low/Medium/High confidence grade
for each of 164 events.

**Live site (GitHub Pages):** https://buffedlizard55-lab.github.io/OLBG1/

## What's inside

| Path | Contents |
|---|---|
| `docs/` | GitHub Pages dashboard (landing + 15 sport pages + High-confidence write-ups + Markets + Methodology + Flagged for Review) |
| `data/matches.csv` · `matches.json` | Full event table; every row links to its OLBG event page |
| `scripts/build_data.py` · `build_site.py` | Reproducible data + site builders |
| `research/` | OLBG structure, methodology, markets investigation, line-by-line verification log |
| `COORDINATION.md` | Multi-session task board (read before contributing) |

## Headline results (snapshot)

- 164 events · 15 sports · **5 High**, 25 Medium, 134 Low confidence.
- High: Leylah Fernandez (Tennis), WAS Wizards (NBA), Afghanistan (Cricket),
  Niels Zonneveld + Dirk van Duijvenbode (Darts, latter flagged F-04).
- Originated prices are model outputs from verified OLBG tip counts only —
  not bookmaker odds (OLBG prices were not visible; left blank, Flag F-03).
- 12 irregularities/limitations published on the Flagged for Review page.

## Rebuild

```bash
python3 scripts/build_data.py
python3 scripts/build_site.py
```

*18+. Betting involves risk; tip popularity is not proof of value. Not financial advice.*
