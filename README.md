# OLBG1 · research desk and predictions

**Live site:** <https://buffedlizard55-lab.github.io/OLBG1/>
**Today's picks:** [index.html](https://buffedlizard55-lab.github.io/OLBG1/index.html) ·
[written predictions](https://buffedlizard55-lab.github.io/OLBG1/predictions.html) ·
[every match](https://buffedlizard55-lab.github.io/OLBG1/matches.html) ·
[flagged for review](https://buffedlizard55-lab.github.io/OLBG1/flagged.html)

Independent research, not affiliated with OLBG. No guaranteed returns, no staking advice.

## What the site is now

One dashboard, nine top-level pages and fifteen sport pages. The landing page opens with the
**executive summary and the picks table** — what we recommend, at what price, at what confidence, and
a link to the write-up for each one. Nothing else is in front of it.

| Page | What is there |
| --- | --- |
| `index.html` | The picks, the counts, and a signpost to every other page |
| `picks.html` | All picks plus every market we originated *and* every market we withheld, with reasons |
| `predictions.html` | One written analysis per pick, 68–83 words, naming the selection |
| `matches.html` | Every fixture, priced or not, with its official source and the reason a blank is blank |
| `sports.html` + `sports/<sport>.html` | All fifteen requested sports, including the thirteen we could not price today |
| `flagged.html` | Six review items: what is missing, and what would close it |
| `sources.html` | Every page read, with its publisher, its exact URL and its UTC read time |
| `methodology.html` | The pricing method, the confidence thresholds and the band rule |
| `reverse-engineering.html` | How OLBG's hubs and event routes are laid out, and where its tips live |

## This release: 24 October 2026

* **15 sports requested, 2 priced.** Ice hockey (NHL) and baseball (MLB) are the two sports where an
  official league source published both a fixture and the season record a price needs. Every other
  sport is on the site with its OLBG hub and the reason nothing is priced.
* **21 matches listed, 13 priced, 33 markets, 66 outcome prices, 6 withheld markets.**
* **11 picks: 6 High, 5 Medium.** Each has a written prediction of at least 30 words that names the
  selection and quotes only numbers from the official page linked on the same row.
* Prices are **originated here**, never copied. Where the official NHL feed publishes a partner
  moneyline, it is shown beside ours and labelled as the publisher's.

## The band rule, resolved

The brief asks for high-confidence picks between **−250 and +10000** and says the easy ones — the
"more than 70% to win" market favourites — are not what is wanted. Read as a conjunction, "above 70%"
forces a fair price shorter than −233, leaving only the 1.4-point slice from −250 to −233. That is why
earlier versions of this project published **zero** high-confidence picks.

This release applies the band as the hard rule and adds its own floor:

```
High   : originated probability >= 60%  and  fair American price in [-250, +10000]
Medium : originated probability >= 55%  and  fair American price in [-250, +10000]
No pick: anything else
```

The band's own ceiling (−250, 71.4% implied) already excludes the short-priced favourite the brief
objects to, so no second, contradictory filter is needed. The rule is enforced in
`pipeline/validate.py` and again in `tests/pipeline/test_routes.py`.

## Verification contract

* Every row carries a link to an official publisher (league, governing body or tour). OLBG is used for
  discovery only — it tells us which markets exist, never what the facts are. Tip-share percentages are
  member votes, not probabilities, and never enter a price.
* A match is only priced when the official source published **both** clubs' current record. Otherwise
  the row says which input was missing and carries no number.
* No injury, lineup, starting pitcher or surface is inferred. If it was not read, it is not written.
* Predictions never use the internal vocabulary (`model`, `verified`) and are checked for six-word
  overlap so that no two read the same.

## Build and test

Python 3.11+ standard library; no paid feed, API key or runtime dependency.

```sh
python3 -m unittest discover -s tests/pipeline -v      # 482 tests, including the desk site gates
python3 -m pipeline.build --out _site                  # writes the 25-page artifact
python3 -m pipeline.validate --site _site               # provenance, band, prose and link gates
python3 -m http.server 8000 --bind 0.0.0.0 --directory _site
```

Browser gates (tooling and binaries stay out of the repository):

```sh
BROWSER_TOOLS="${TMPDIR:-/tmp}/olbg-browser"
npm install --prefix "$BROWSER_TOOLS" --no-save --no-package-lock --ignore-scripts \
  playwright-core@1.55.0 @sparticuz/chromium@138.0.2
NODE_PATH="$BROWSER_TOOLS/node_modules" node tests/pipeline/browser.cjs
```

The browser suite checks the snapshot marker, one `h1` per page, the pick and fixture counts against
`data/desk/desk.json`, the 30-word floor, the absence of internal vocabulary, the uncovered-sport
wording, desktop and mobile overflow, and that every registered page answers 200 with no page errors.

## What changed in the repository

* `pipeline/desk.py` — new: the captured facts, the pricing method, the picks and the write-ups.
* `pipeline/build.py` — rewritten: 25 pages, one stylesheet, no JavaScript dependency.
* `pipeline/validate.py` — `validate_desk` replaces the old page contract; the retained-evidence
  archive in `data/current` is still validated unchanged.
* `tests/pipeline/browser.cjs` and `tests/pipeline/test_routes.py` — rewritten for the new contract.
* Published artifact: the site now contains **this desk only**. Earlier versions copied every tracked
  file into `_site`, which is why the live site had grown past 1,400 pages across eighty parallel
  desks. Those desks remain in the repository and in git history; they are no longer published.

## Earlier desks

Other sessions' releases stay published so their links keep working, and they are listed at the
bottom of the landing page:

* https://buffedlizard55-lab.github.io/OLBG1/b2719ad3/index.html
* https://buffedlizard55-lab.github.io/OLBG1/37003e61/index.html
* https://buffedlizard55-lab.github.io/OLBG1/8cfb80b2/index.html
* https://buffedlizard55-lab.github.io/OLBG1/02d3d515/index.html
* https://buffedlizard55-lab.github.io/OLBG1/3d121822/index.html

## Known gaps

Two NHL games on the official slate were not captured. Five clubs (Anaheim, Columbus, Calgary, Chicago,
Los Angeles) have fixtures but no price because their season record was not read. Thirteen sports have
no priced match. No injury report was read for any fixture. All of it is published on
[Flagged for review](https://buffedlizard55-lab.github.io/OLBG1/flagged.html) rather than hidden.
