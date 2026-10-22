#!/usr/bin/env python3
"""Strict, dependency-free verification gate for the primary OLBG desk.

The gate deliberately distinguishes between two things:

* source-backed facts in the primary dataset, row by row, including each row's verification ledger; and
* model outputs, which are labelled as independently originated estimates.

It checks every primary fixture source against a maintained official-authority host
allowlist, market completeness (or an explicit blank/unverified exception), high-pick
writing rules, generated-export consistency, the root/mirror data copies, and every
relative link across every published HTML page in the repository.

No network request is made here.  A successful run confirms the audited snapshot and
its source links are structurally complete and reproducible; it does not claim that a
remote publisher has not subsequently changed a page.
"""
from __future__ import annotations

import csv
import hashlib
import json
import re
import sys
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent

errors: list[str] = []
warnings: list[str] = []

EXCLUDED_SLUGS = {
    "football", "soccer", "horse-racing", "american-football",
    "boxing", "ufc", "mma", "ufc-mma", "specials", "entertainment",
    "hurling", "cycling",
}

# These are the official governing-body, league, tour, federation and organiser
# domains actually used by data/fixtures.json.  OLBG is intentionally absent: it is
# an upstream-discovery source and cannot verify a sporting fact in this data model.
OFFICIAL_FIXTURE_HOSTS = {
    "api-web.nhle.com",
    "ehfcl.eurohandball.com",
    "gaacork.ie",
    "lolesports.com",
    "munster.gaa.ie",
    "scoring.nzc.nz",
    "statsapi.mlb.com",
    "top14.lnr.fr",
    "www.afl.com.au",
    "www.atptour.com",
    "www.cricket.com.au",
    "www.eurohandball.com",
    "www.euroleaguebasketball.net",
    "www.europeantour.com",
    "www.formula1.com",
    "www.galwaygaa.ie",
    "www.gbgb.org.uk",
    "www.icc-cricket.com",
    "www.intrl.sport",
    "www.legavolley.it",
    "www.lpga.com",
    "www.mlb.com",
    "www.nba.com",
    "www.nhl.com",
    "www.nrl.com",
    "www.pdc.tv",
    "www.pgatour.com",
    "www.plusliga.pl",
    "www.premrugby.com",
    "www.unitedrugby.com",
    "www.wst.tv",
    "www.wtatennis.com",
}


class LinkAndRowCollector(HTMLParser):
    """Collect href/src values and links occurring in each body table row."""

    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []
        self._tbody_depth = 0
        self._tr_depth = 0
        self.row_links: list[list[str]] = []
        self._row: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        a = dict(attrs)
        if tag == "tbody":
            self._tbody_depth += 1
        elif tag == "tr" and self._tbody_depth:
            self._tr_depth += 1
            self._row = []

        if tag == "a" and a.get("href") is not None:
            href = str(a["href"])
            self.links.append(href)
            if self._tr_depth:
                self._row.append(href)
        elif tag in ("link", "script", "img"):
            target = a.get("href") or a.get("src")
            if target is not None:
                self.links.append(str(target))

    def handle_endtag(self, tag: str) -> None:
        if tag == "tr" and self._tr_depth:
            self._tr_depth -= 1
            self.row_links.append(self._row)
        elif tag == "tbody" and self._tbody_depth:
            self._tbody_depth -= 1


def load_json(relative: str) -> dict:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def is_official_url(url: str) -> bool:
    parsed = urlparse(url)
    return parsed.scheme == "https" and parsed.hostname in OFFICIAL_FIXTURE_HOSTS


def check_official_source(source: dict, context: str) -> None:
    name = str(source.get("name", "")).strip()
    url = str(source.get("url", "")).strip()
    if not name:
        errors.append(f"{context}: official source has no name")
    if not url.startswith("https://"):
        errors.append(f"{context}: official source is not HTTPS -> {url!r}")
    elif not is_official_url(url):
        errors.append(f"{context}: source host is not in official allowlist -> {url}")


def resolve_internal(page: Path, href: str) -> Path | None:
    """Resolve an internal static-site path, accepting a directory's index.html."""
    clean = href.split("#", 1)[0].split("?", 1)[0]
    if not clean:
        return None
    # The project is served at /OLBG1/ on GitHub Pages.  Resolve its few base-path
    # absolute links to the checkout while still rejecting other absolute filesystem paths.
    if clean.startswith("/OLBG1/"):
        candidate = ROOT / clean.removeprefix("/OLBG1/")
    elif clean.startswith("/"):
        return Path("/__outside_site__")
    else:
        candidate = (page.parent / clean).resolve()
    if candidate.is_dir():
        candidate = candidate / "index.html"
    return candidate


def check_all_html_links() -> int:
    """Verify every relative link across all published workspaces, not just root."""
    pages = sorted(ROOT.rglob("*.html"))
    for page in pages:
        rel = page.relative_to(ROOT).as_posix()
        parser = LinkAndRowCollector()
        parser.feed(page.read_text(encoding="utf-8"))
        for href in parser.links:
            if not href:
                errors.append(f"{rel}: empty href/src")
                continue
            if href.startswith(("https://", "mailto:", "tel:", "javascript:", "#")):
                continue
            if href.startswith("http://"):
                errors.append(f"{rel}: non-HTTPS external URL -> {href}")
                continue
            dest = resolve_internal(page, href)
            if dest is None:
                continue
            try:
                dest.resolve().relative_to(ROOT.resolve())
            except ValueError:
                errors.append(f"{rel}: link escapes repository root -> {href}")
                continue
            if not dest.is_file():
                errors.append(f"{rel}: broken internal link -> {href} (expected {dest})")
    return len(pages)


def check_primary_table_source_links() -> None:
    """Every row in the primary data tables needs at least one external source link."""
    pages = [ROOT / "picks.html", ROOT / "flagged.html", *sorted((ROOT / "sports").glob("*.html"))]
    pages += [ROOT / "f7fa77fc" / "picks.html", ROOT / "f7fa77fc" / "flagged.html"]
    pages += sorted((ROOT / "f7fa77fc" / "sports").glob("*.html"))
    for page in pages:
        parser = LinkAndRowCollector()
        parser.feed(page.read_text(encoding="utf-8"))
        for index, row_links in enumerate(parser.row_links, 1):
            if not any(href.startswith("https://") for href in row_links):
                if any(href.startswith("methodology.html") for href in row_links):
                    # A methodology/policy finding cites our own rulebook: no governing body
                    # publishes a source for our margin policy, and dressing a league page up
                    # as proof would be worse than saying so.  Disclosed as a warning.
                    warnings.append(
                        f"{page.relative_to(ROOT)}: table row #{index} cites the methodology page "
                        f"instead of an external official source (internal policy finding)"
                    )
                    continue
                errors.append(f"{page.relative_to(ROOT)}: table row #{index} has no HTTPS source link")


def check_data_and_predictions() -> tuple[int, int, int]:
    css_txt = (ROOT / "site_src" / "style.css").read_text(encoding="utf-8")
    if "linear-gradient" in css_txt:
        errors.append("site_src/style.css still contains linear-gradient")

    fixtures_doc = load_json("data/fixtures.json")
    lines_doc = load_json("data/lines.json")
    predictions_doc = load_json("data/predictions.json")
    sources_doc = load_json("data/sources.json")
    taxonomy_doc = load_json("data/olbg_taxonomy.json")

    fixtures = fixtures_doc["fixtures"]
    lines = lines_doc["lines"]
    preds = predictions_doc["predictions"]

    if fixtures_doc.get("count") != len(fixtures):
        errors.append("fixtures count metadata does not equal fixture rows")
    if lines_doc.get("count") != len(lines):
        errors.append("lines count metadata does not equal line rows")
    if predictions_doc.get("count") != len(preds):
        errors.append("predictions count metadata does not equal prediction rows")

    in_scope_tax = [sport for sport in taxonomy_doc["sports"] if sport["in_scope"]]
    if len(in_scope_tax) != 17:
        errors.append(f"Expected 17 in-scope sports in olbg_taxonomy.json, got {len(in_scope_tax)}")

    registry = sources_doc.get("sources", [])
    if not registry:
        errors.append("official source registry is empty")
    for source in registry:
        source_id = source.get("id", "<missing>")
        url = str(source.get("url", ""))
        if source_id == "olbg":
            if urlparse(url).hostname != "www.olbg.com":
                errors.append(f"source registry {source_id}: expected OLBG upstream URL, got {url}")
        else:
            check_official_source(source, f"source registry {source_id}")

    seen_ids: set[str] = set()
    fixtures_by_id: dict[str, dict] = {}
    for fixture in fixtures:
        fixture_id = fixture.get("id")
        if not fixture_id or fixture_id in seen_ids:
            errors.append(f"invalid or duplicate fixture id: {fixture_id}")
            continue
        seen_ids.add(fixture_id)
        fixtures_by_id[fixture_id] = fixture
        if fixture.get("sport") in EXCLUDED_SLUGS:
            errors.append(f"{fixture_id}: excluded sport leaked into dataset: {fixture['sport']}")
        if fixture.get("status") not in ("verified", "cross-checked", "unverified"):
            errors.append(f"{fixture_id}: invalid status {fixture.get('status')}")
        fixture_sources = fixture.get("sources", [])
        if not fixture_sources:
            errors.append(f"{fixture_id}: missing governing-body source")
        for source in fixture_sources:
            check_official_source(source, fixture_id)
        # Every row must carry a verification ledger entry, and any row claiming to have
        # been re-checked must point at the HTTPS page that was actually read.
        vblock = fixture.get("verification")
        if not isinstance(vblock, dict):
            errors.append(f"{fixture_id}: missing verification ledger block")
        else:
            verdict = vblock.get("verdict")
            if verdict not in ("confirmed", "corrected", "conflict", "unconfirmed", "blocked", "not-rechecked"):
                errors.append(f"{fixture_id}: invalid verification verdict {verdict!r}")
            if verdict in ("confirmed", "corrected", "conflict", "blocked", "unconfirmed"):
                ev = str(vblock.get("evidence", ""))
                if not ev.startswith("https://"):
                    errors.append(f"{fixture_id}: verification evidence is not an HTTPS page -> {ev!r}")
                if not vblock.get("checked_utc"):
                    errors.append(f"{fixture_id}: verification block has no checked_utc")
            if verdict in ("confirmed", "corrected") and not vblock.get("fields"):
                errors.append(f"{fixture_id}: confirmed row lists no confirmed fields")

    lines_by_id = {line.get("id"): line for line in lines}
    if len(lines_by_id) != len(lines) or None in lines_by_id:
        errors.append("invalid or duplicate originated-line IDs")
    # A fixture carrying both sides is normally priced; rows explicitly marked unpriced
    # (no verified inputs yet) are published as event cards instead of guessed lines.
    h2h_ids = {
        fixture["id"] for fixture in fixtures if fixture.get("away") and not fixture.get("unpriced")
    }
    if set(lines_by_id) != h2h_ids:
        errors.append(f"H2H fixtures ({len(h2h_ids)}) != priced lines ({len(lines_by_id)})")

    valid_confidence = {"high", "medium", "low"}
    valid_market_keys = {
        "winner", "dnb", "handicap", "total",
        # T41 ladder rungs: two alternate handicap lines and two alternate totals
        "handicap_alt_1", "handicap_alt_2", "total_low", "total_high",
    }
    # The brief's high-confidence price window, restated here so the gate does not have to
    # import the model to police it.
    window_min, window_max = -250, 10000

    def american_of(dec: float) -> int:
        if dec >= 2.0:
            return int(round((dec - 1.0) * 100))
        return -int(round(100.0 / max(dec - 1.0, 0.01)))
    for line_id, line in lines_by_id.items():
        fixture = fixtures_by_id.get(line_id)
        if fixture is None:
            errors.append(f"{line_id}: pricing has no fixture")
            continue
        if line.get("confidence") not in valid_confidence:
            errors.append(f"{line_id}: invalid confidence {line.get('confidence')}")
        markets = line.get("markets", [])
        market_keys = [market.get("key") for market in markets]
        if len(market_keys) != len(set(market_keys)):
            errors.append(f"{line_id}: duplicate market key")
        if any(key not in valid_market_keys for key in market_keys):
            errors.append(f"{line_id}: unknown market key(s) {market_keys}")
        if not {"winner", "handicap"}.issubset(market_keys):
            errors.append(f"{line_id}: missing required winner/handicap market ({market_keys})")

        winner = next((market for market in markets if market.get("key") == "winner"), None)
        if not winner:
            continue
        winner_outcomes = winner.get("outcomes", [])
        priced_selections = {
            outcome.get("selection") for market in markets for outcome in market.get("outcomes", [])
        }
        if line.get("pick") not in priced_selections:
            errors.append(f"{line_id}: pick {line.get('pick')} is not a priced selection")
        if len(winner_outcomes) == 3 and "dnb" not in market_keys:
            errors.append(f"{line_id}: three-way winner market must include Draw No Bet")
        if len(winner_outcomes) not in (2, 3):
            errors.append(f"{line_id}: winner market must have 2 or 3 outcomes")

        unavailable = line.get("unavailable_markets", [])
        unavailable_keys = [market.get("key") for market in unavailable]
        if len(unavailable_keys) != len(set(unavailable_keys)):
            errors.append(f"{line_id}: duplicate unavailable market key")
        if set(market_keys) & set(unavailable_keys):
            errors.append(f"{line_id}: a market cannot be both priced and unavailable")
        for market in unavailable:
            if market.get("status") != "unverified" or not str(market.get("reason", "")).strip():
                errors.append(f"{line_id}: unavailable market needs unverified status and a reason")
        if "total" not in market_keys:
            total_exception = next((market for market in unavailable if market.get("key") == "total"), None)
            if not total_exception:
                errors.append(f"{line_id}: missing total without explicit unverified exception")
            elif not any("total" in flag.lower() for flag in fixture.get("flags", [])):
                errors.append(f"{line_id}: blank total is not exposed on its fixture flag")

        for market in markets:
            outcomes = market.get("outcomes", [])
            if len(outcomes) < 2:
                errors.append(f"{line_id}/{market.get('key')}: fewer than two outcomes")
                continue
            probability_sum = sum(float(outcome.get("probability", 0)) for outcome in outcomes)
            if abs(probability_sum - 1.0) > 1e-5:
                errors.append(f"{line_id}/{market.get('key')}: probability sum {probability_sum} != 1.0")
            for outcome in outcomes:
                if not str(outcome.get("selection", "")).strip():
                    errors.append(f"{line_id}/{market.get('key')}: blank outcome selection")
                odds = outcome.get("odds")
                fair_odds = outcome.get("fair_odds")
                if not isinstance(odds, (int, float)) or not (1.01 < odds < 100.0):
                    errors.append(f"{line_id}/{market.get('key')}: implausible odds {odds}")
                if not isinstance(fair_odds, (int, float)) or not (1.01 <= fair_odds < 100.0):
                    errors.append(f"{line_id}/{market.get('key')}: implausible fair odds {fair_odds}")

    high_ids = {line_id for line_id, line in lines_by_id.items() if line.get("confidence") == "high"}
    for line_id in high_ids:
        fixture = fixtures_by_id[line_id]
        line = lines_by_id[line_id]
        if fixture.get("status") != "verified":
            errors.append(f"{line_id}: high confidence requires verified fixture status")
        if not line.get("both_measured") or line.get("rating_coverage") != 2:
            errors.append(f"{line_id}: high confidence requires two measured official ratings")
        # --- T41: the high-confidence price window is mandatory, not advisory -----------
        if not line.get("pick_in_window"):
            errors.append(f"{line_id}: high-confidence pick is outside the -250/+10000 window")
        window = line.get("window") or {}
        if window.get("min_american") != window_min or window.get("max_american") != window_max:
            errors.append(f"{line_id}: window block missing or wrong ({window})")
        pick_odds = line.get("pick_odds")
        if not isinstance(pick_odds, (int, float)):
            errors.append(f"{line_id}: high-confidence pick has no published price")
        else:
            american = american_of(float(pick_odds))
            if not (window_min <= american <= window_max):
                errors.append(
                    f"{line_id}: published price {pick_odds} ({american}) is outside the "
                    f"-250/+10000 window"
                )
        floor = float(window.get("conviction_floor") or 0)
        probability = line.get("pick_probability")
        if not isinstance(probability, (int, float)) or probability < floor:
            errors.append(
                f"{line_id}: high-confidence pick probability {probability} below the "
                f"{floor:.2f} conviction floor"
            )

    pred_by_id = {prediction.get("match_id"): prediction for prediction in preds}
    if len(pred_by_id) != len(preds) or None in pred_by_id:
        errors.append("invalid or duplicate prediction match IDs")
    if set(pred_by_id) != high_ids:
        errors.append(f"high picks ({len(high_ids)}) != predictions ({len(pred_by_id)})")

    ngrams: Counter[tuple[str, ...]] = Counter()
    for match_id, prediction in pred_by_id.items():
        line = lines_by_id.get(match_id)
        if not line:
            errors.append(f"{match_id}: prediction has no originated line")
            continue
        words = prediction.get("text", "").split()
        if len(words) < 30:
            errors.append(f"{match_id}: prediction has {len(words)} words (<30 minimum)")
        if prediction.get("selection") != line.get("pick"):
            errors.append(f"{match_id}: prediction selection does not equal model pick")
        if str(line.get("pick", "")).lower() not in prediction.get("text", "").lower():
            errors.append(f"{match_id}: selected pick missing from prediction prose")
        bet_line = prediction.get("bet_line", "")
        if str(line.get("pick")) not in bet_line:
            errors.append(f"{match_id}: bet_line does not quote the model pick")
        if f"{float(line.get('pick_odds', 0)):.2f}" not in bet_line:
            errors.append(f"{match_id}: bet_line price drifted from the model price")
        if not prediction.get("in_window"):
            errors.append(f"{match_id}: high-confidence prediction is not flagged in-window")
        sources = prediction.get("sources", [])
        if not sources:
            errors.append(f"{match_id}: prediction missing official source")
        for source in sources:
            check_official_source(source, f"prediction {match_id}")
        tokens = [re.sub(r"^[^\w]+|[^\w]+$", "", word.lower()) for word in words]
        tokens = [token for token in tokens if token]
        for index in range(len(tokens) - 5):
            ngrams[tuple(tokens[index : index + 6])] += 1
    duplicates = {gram: count for gram, count in ngrams.items() if count > 1}
    if duplicates:
        errors.append(f"duplicate 6-word n-grams in predictions: {duplicates}")

    # The machine-readable full export must contain the same primary IDs and prices.
    full_doc = load_json("datasets/matches_full.json")
    full_rows = full_doc.get("matches", [])
    if full_doc.get("count") != len(full_rows) or {row.get("id") for row in full_rows} != seen_ids:
        errors.append("datasets/matches_full.json is not a complete primary-fixture export")
    for row in full_rows:
        if row.get("is_h2h") and not row.get("pricing") and not row.get("unpriced"):
            errors.append(f"{row.get('id')}: full export lost H2H pricing")

    with (ROOT / "datasets" / "matches_full.csv").open(encoding="utf-8", newline="") as handle:
        csv_rows = list(csv.DictReader(handle))
    if len(csv_rows) != len(fixtures) or {row.get("id") for row in csv_rows} != seen_ids:
        errors.append("datasets/matches_full.csv is not a complete primary-fixture export")

    # The mirror is a byte-for-byte publication of primary JSON, avoiding drift.
    for filename in ("fixtures.json", "lines.json", "predictions.json", "olbg_taxonomy.json", "sources.json", "coverage.json"):
        primary = ROOT / "data" / filename
        mirror = ROOT / "f7fa77fc" / "data" / filename
        if not mirror.is_file():
            errors.append(f"f7fa77fc mirror missing data/{filename}")
        elif hashlib.sha256(primary.read_bytes()).digest() != hashlib.sha256(mirror.read_bytes()).digest():
            errors.append(f"f7fa77fc mirror drift in data/{filename}")

    for sport in load_json("data/coverage.json")["included"]:
        slug = sport["sport"]
        for base in (ROOT, ROOT / "f7fa77fc"):
            page = base / "sports" / f"{slug}.html"
            if not page.is_file():
                errors.append(f"missing sport subpage: {page.relative_to(ROOT)}")

    return len(fixtures), len(lines), len(preds)


def main() -> int:
    fixture_count, line_count, prediction_count = check_data_and_predictions()
    html_count = check_all_html_links()
    check_primary_table_source_links()

    print(
        f"Primary data: {fixture_count} fixtures | {line_count} H2H line books | "
        f"{prediction_count} high-confidence predictions"
    )
    print(f"Validated relative links across {html_count} published HTML pages")
    print(f"Errors: {len(errors)}   Warnings: {len(warnings)}")
    for warning in warnings[:20]:
        print("  WARN:", warning)
    for error in errors[:40]:
        print("  ERR :", error)
    if errors:
        print("\nVALIDATION FAILED")
        return 1
    print("\nVALIDATION PASSED — primary provenance, exports, markets, writing rules, and site links are consistent")
    return 0


if __name__ == "__main__":
    sys.exit(main())
