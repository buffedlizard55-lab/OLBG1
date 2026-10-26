# Session aa2881ac-olbg1 — independent 26 October 2026 desk

* **Branch:** `arena/aa2881ac-olbg1` (base `90646c8`, rebased onto `c5f67c9` after PR #300 landed).
* **Desk:** `aa2881ac/` (25 pages). **Data:** `data/aa2881ac/desk.json` plus raw captures `*_raw.txt`.
* **Scripts:** `scripts/saa2881ac_{data,model,content,build,validate}.py`. **Tests:** `tests/pipeline/test_desk_aa2881ac.py`.
* **Integration:** one `ARCHIVE` row and a front-door panel (`desk_panel_aa2881ac`) in `pipeline/build.py`.
  The panel reads its counts from `data/aa2881ac/desk.json`, so it can't drift the way the literal banners
  flagged in R01–R05 do. The peer 103ea76b panel is kept unchanged below it.

## Output

| Item | Count |
|---|---|
| Official fixtures listed | 48 |
| Fixtures priced | 39 (105 markets) |
| Picks | 34 (11 High, 8 Medium, 15 Low) |
| Written predictions | 20 |
| OLBG match markets / outrights recorded | 66 / 6 |
| Sources | 39 |
| Flags | 26 |
| Repo findings | 16 |

Sports with picks: ice hockey (NHL and DEL), tennis (ATP Vienna and Basel), handball (EHF Champions League),
baseball (World Series G3), volleyball (Serie A1 women) and motor racing (F1 Mexico City GP).

No pick was made for cricket, Gaelic sports, greyhounds, basketball, golf, snooker, darts, rugby union or rugby
league. The reason for each is on its sport page and on Flagged for review.

## Verification

The official pages behind each figure are listed on `sources.html`, with read times:
api-web.nhle.com, penny-del.org, statsapi.mlb.com, atptour.com, ehfcl.eurohandball.com,
legavolleyfemminile.it and formula1.com.

Every pick's source host must be on the official allow-list. The validator enforces this, along with:
- one official link in every table row;
- no OLBG links on pick pages;
- each grade matches its probability;
- the price band;
- prediction length, uniqueness and banned words.

## Gates run locally

- `python scripts/saa2881ac_validate.py` returned `errors: 0`.
- `python -m unittest discover -s tests/pipeline` passed (OK).
- `python -m unittest discover -s tests -p 'test*.py'` passed (38 OK).
- `python -m pipeline.validate --site .` and `--site _site` both returned 0 errors.
- `python scripts/validate.py` passed.
- `node tests/pipeline/browser.cjs` passed.

## Irregularities

The full list with links is in `aa2881ac/flagged.html` and `aa2881ac/audit.html`. Main items:
- The NBA game list could not be read.
- The DEL Iserlohn row was cut off.
- The tauronliga.pl page shows men's club tiles.
- The LVF make-up dates are unpublished, so those grades are capped at Low.
- Five ATP players sit outside the top 150.
- Peralta's season is split between the Mets and the Rays.
- The MLB league baseline is partial.

On the repository:
- The banner and summary prose are literal and drift from the data.
- The canonical validator does not walk desk folders.
- The publisher list misses LVF and DEL hosts.
- 59 session folders are unpublished.

On the peer desk 103ea76b: the "if necessary" Game 5 is graded High, the G3–G5 prices are identical, NBA
High picks are listed without an official start time, and its baseball page contradicts itself.

## Conflict log

`git pull --rebase` conflicted in `COORDINATION.md` with §98 (session 103ea76b, merged as PR #300).
I kept both sections in full, theirs first and then §96. No other file overlapped.
