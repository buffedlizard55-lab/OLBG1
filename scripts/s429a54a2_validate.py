#!/usr/bin/env python3
"""Validator for the 429a54a2-olbg1 desk. Exits 1 on any failed assertion."""

from __future__ import annotations

import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DESK = ROOT / "429a54a2"
DATA = ROOT / "data" / "429a54a2"

ALLOWED_HOSTS = {
    "api-web.nhle.com", "www.nhl.com", "www.pgatour.com", "www.atptour.com", "wtafiles.wtatennis.com",
    "www.pdctv.tv", "www.pdc.tv", "www.wst.tv", "www.cricket.com.au", "prod2.lnr.fr", "www.lnr.fr",
    "stats.unitedrugby.com", "www.unitedrugby.com", "lnh.fr", "www.lnh.fr", "www.bathrugby.com", "www.gloucesterrugby.co.uk",
    "www.newcastleredbulls.com", "en.rugby-japan.jp", "www.intrl.sport", "statsapi.mlb.com", "www.nba.com",
    "www.euroleaguebasketball.net", "gaacork.ie", "www.galwaygaa.ie", "kilkennygaa.ie", "munster.gaa.ie",
    "www.gbgb.org.uk", "api.gbgb.org.uk", "www.volleyball-bundesliga.de", "www.skra.pl",
    "www.legavolley.it", "www.flamengo.com.br", "www.fcbarcelona.com", "www.tbv-lemgo-lippe.de",
    "www.formula1.com", "www.opel-hbl.de", "cbv.com.br", "www.icc-cricket.com",
}

errors: list[str] = []


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.hrefs = []
        self.row_links = []
        self._in_tr = 0
        self._row = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "tr":
            self._in_tr += 1
            self._row = []
        if tag == "a" and a.get("href"):
            self.hrefs.append(a["href"])
            if self._in_tr:
                self._row.append(a["href"])
        if tag in ("link", "script", "img"):
            for key in ("href", "src"):
                if a.get(key):
                    self.hrefs.append(a[key])

    def handle_endtag(self, tag):
        if tag == "tr" and self._in_tr:
            self._in_tr -= 1
            self.row_links.append(self._row)


def check(cond, msg):
    if not cond:
        errors.append(msg)


def main():
    fixtures = json.loads((DATA / "fixtures.json").read_text())
    preds = json.loads((DATA / "predictions.json").read_text())
    summary = json.loads((DATA / "summary.json").read_text())
    flagged = json.loads((DATA / "flagged.json").read_text())

    ids = [f["id"] for f in fixtures]
    check(len(ids) == len(set(ids)), "duplicate fixture id")

    for f in fixtures:
        check(f["official_url"].startswith("https://"), f"{f['id']}: official url not https")
        host = f["official_url"].split("/")[2]
        if f["status"] == "unverified":
            check(host in ALLOWED_HOSTS or host == "www.olbg.com",
                  f"{f['id']}: unverified row must cite an official page or the OLBG discovery card")
        else:
            check(host in ALLOWED_HOSTS, f"{f['id']}: host not an official publisher -> {host}")
        check(bool(f["official_label"]), f"{f['id']}: missing source label")
        check(bool(f["observed"]), f"{f['id']}: missing observation window")
        check(f["status"] in ("verified", "unverified", "elapsed"), f"{f['id']}: bad status")
        if f["status"] != "verified":
            check(not f["price"]["markets"], f"{f['id']}: non-verified row carries a price")
            check(f["price"]["selection"] is None, f"{f['id']}: non-verified row carries a selection")
        p = f["price"]
        if p["markets"]:
            check(bool(p["basis"]), f"{f['id']}: priced row without a stated basis")
            check(p["probability"] is not None and 0 < p["probability"] < 1, f"{f['id']}: bad probability")
            check(abs(p["fair_decimal"] * p["probability"] - 1) < 1e-9, f"{f['id']}: price is not 1/p")
            for m in p["markets"]:
                q = m["probability"]
                check(q is not None and 0 < q < 1, f"{f['id']}: market probability out of range")
                check(abs(m["fair_decimal"] * q - 1) < 1e-9, f"{f['id']}: market price is not 1/p")
                check(isinstance(m["american"], int), f"{f['id']}: market american price missing")
            winners = [m for m in p["markets"] if m["market"] == "match_winner"]
            if winners:
                check(abs(sum(m["probability"] for m in winners) - 1) < 1e-6, f"{f['id']}: two-way mass is not 1")
            three = [m for m in p["markets"] if m["market"] == "match_winner_3way"]
            if three:
                check(abs(sum(m["probability"] for m in three) - 1) < 1e-6, f"{f['id']}: three-way mass is not 1")
            if p["tier"] == "High":
                check(p["probability"] >= 0.70, f"{f['id']}: High below 0.70")
                check(1.40 <= p["fair_decimal"] <= 101.0, f"{f['id']}: in-band High outside -250..+10000")
            if (p["tier"] or "").startswith("High ("):
                check(p["probability"] >= 0.70, f"{f['id']}: out-of-band High below 0.70")
                check(p["fair_decimal"] < 1.40, f"{f['id']}: out-of-band High is actually inside the band")
            if p["tier"] == "Medium":
                check(0.60 <= p["probability"] < 0.70, f"{f['id']}: Medium probability outside 0.60-0.70")

    by_id = {f["id"]: f for f in fixtures}
    seen_text = []
    for p in preds:
        words = p["text"].split()
        check(len(words) >= 30, f"{p['id']}: under 30 words")
        for bad in ("model", "verified"):
            check(not re.search(rf"\b{bad}\b", p["text"], re.I), f"{p['id']}: forbidden internal word '{bad}'")
        check(p["fixture"] in by_id, f"{p['id']}: unknown fixture")
        if p["fixture"] in by_id:
            f = by_id[p["fixture"]]
            check(bool(f["price"]["markets"]), f"{p['id']}: prediction on an unpriced fixture")
            check(p["selection"], f"{p['id']}: no selection named")
        tokens = re.findall(r"[a-z0-9']+", p["text"].lower())
        grams = {" ".join(tokens[i:i + 6]) for i in range(len(tokens) - 5)}
        for other in seen_text:
            check(not (grams & other), f"{p['id']}: shares a six-word phrase with an earlier prediction")
        seen_text.append(grams)

    counts = summary["counts"]
    check(counts["rows"] == len(fixtures), "row count mismatch")
    check(counts["priced"] == sum(1 for f in fixtures if f["price"]["markets"]), "priced count mismatch")
    check(counts["high"] == sum(1 for f in fixtures if f["price"]["tier"] == "High"), "High count mismatch")
    check(counts["high_out"] == sum(1 for f in fixtures if (f["price"]["tier"] or "").startswith("High (")), "out-of-band count mismatch")
    check(counts["predictions"] == len(preds), "prediction count mismatch")
    check(counts["flags"] == len(flagged), "flag count mismatch")
    check(counts["sports"] == 15, "sport count must be 15")

    pages = sorted(DESK.rglob("*.html"))
    check(len(pages) >= 25, f"expected at least 25 pages, found {len(pages)}")
    for page in pages:
        text = page.read_text(encoding="utf-8")
        parser = Links()
        parser.feed(text)
        check("<h1>" in text, f"{page.name}: no h1")
        for href in parser.hrefs:
            if href.startswith(("https://", "mailto:")):
                continue
            check(not href.startswith("http://"), f"{page.name}: non-https external link {href}")
            target = (page.parent / href.split("#")[0]).resolve() if href.split("#")[0] else page
            if target.is_dir():
                target = target / "index.html"
            check(target.is_file(), f"{page.name}: broken internal link {href}")
        # Every table row on the desk pages must carry an external source link.
        for i, links in enumerate(parser.row_links, 1):
            if not links:
                continue
            check(any(h.startswith("https://") for h in links), f"{page.name}: table row {i} has no external source link")

    # A page must exist for each of the 15 sports.
    for slug in ["golf", "volleyball", "rugby-union", "cricket", "snooker", "darts", "baseball",
                 "gaelic-sports", "greyhounds", "tennis", "motor-racing", "handball", "ice-hockey",
                 "basketball", "rugby-league"]:
        check((DESK / "sports" / f"{slug}.html").is_file(), f"missing sport page {slug}")

    for err in errors:
        print("ERROR:", err)
    print(f"VALIDATION {'FAILED' if errors else 'PASSED'} — {len(fixtures)} rows, {len(pages)} pages, {len(preds)} predictions, {len(errors)} errors")
    raise SystemExit(bool(errors))


if __name__ == "__main__":
    main()
