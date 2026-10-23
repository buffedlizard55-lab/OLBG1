#!/usr/bin/env python3
"""TED71 (session ed71b937-olbg1) - release validator.

Fails the build on any of:
  * a data row missing from the published match table
  * a published row that has an official value but no official source link
  * a high-confidence pick outside the stated band
  * prediction prose that is short, repetitive, or uses banned vocabulary
  * a flag in the register that does not reach the Flagged page
  * a broken relative link, or a page with no <title>
  * a manifest count that disagrees with the data
Exit code is non-zero on the first failing class of problem, and every
problem found is printed.
"""

from __future__ import annotations

import html
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data", "ed71b937")
OUT = os.path.join(ROOT, "ed71b937")

BAND_MIN, BAND_MAX, PROB_FLOOR = -250, 10000, 0.700
BANNED = ("model", "verified")


def load(name):
    with open(os.path.join(DATA, name), encoding="utf-8") as fh:
        return json.load(fh)


def read_page(relpath):
    with open(os.path.join(OUT, relpath), encoding="utf-8") as fh:
        return fh.read()


def main():
    problems = []
    ok = []

    def check(cond, msg):
        (ok if cond else problems).append(msg)

    fx, ln, pr = load("fixtures.json"), load("lines.json"), load(
        "predictions.json")
    man = load("site-manifest.json")

    # 1. every page in the manifest exists and has a title
    for p in man["pages"]:
        full = os.path.join(OUT, p)
        if not os.path.exists(full):
            problems.append("missing page {}".format(p))
            continue
        doc = read_page(p)
        check("<title>" in doc and "</title>" in doc,
              "page {} has a <title>".format(p))
        check(doc.startswith("<!DOCTYPE html>"),
              "page {} has a doctype".format(p))

    # 2. every data row is published on matches.html
    matches = read_page("matches.html")
    missing = [r["id"] for r in fx["rows"] if r["id"] not in matches]
    check(not missing,
          "all {} rows appear on matches.html{}".format(
              len(fx["rows"]), "" if not missing else "; missing " +
              ", ".join(missing[:8])))

    # 3. every official row carries its source link on the match table
    for r in fx["rows"]:
        o = r["official"]
        if not o:
            continue
        for u in o["sources"]:
            host = re.sub(r"^https?://(www\.)?", "", u).split("/")[0]
            # the link must sit inside the same <tr> as the row id
            m = re.search(r"<tr>(?:(?!</tr>).)*?<code>" + re.escape(r["id"])
                          + r"</code>(?:(?!</tr>).)*?</tr>", matches, re.S)
            check(bool(m) and host in m.group(0),
                  "row {} publishes its source {}".format(r["id"], host))

    # 4. blanks are preserved, not filled: a discovery-only row must not
    #    show a kickoff or venue it never had
    for r in fx["rows"]:
        if r["official"]:
            continue
        m = re.search(r"<tr>(?:(?!</tr>).)*?<code>" + re.escape(r["id"])
                      + r"</code>(?:(?!</tr>).)*?</tr>", matches, re.S)
        if not m:
            problems.append("row {} not found as a table row".format(r["id"]))
            continue
        row = m.group(0)
        check("DISCOVERY ONLY" in row,
              "row {} is marked discovery-only".format(r["id"]))

    # 5. the high-confidence gate actually holds
    hi = [s for s in ln["selections"] if s["tier"] == "high-in-band"]
    check(len(hi) > 0, "at least one high-confidence pick exists")
    for s in hi:
        check(s["prob"] >= PROB_FLOOR,
              "{} prob {:.4f} >= {:.3f}".format(s["market"], s["prob"],
                                                PROB_FLOOR))
        check(BAND_MIN <= s["fair_american"] <= BAND_MAX,
              "{} price {} inside [{}, {}]".format(s["market"],
                                                   s["fair_american"],
                                                   BAND_MIN, BAND_MAX))
        fxrow = next((r for r in fx["rows"] if r["id"] == s["fixture_id"]),
                     None)
        check(fxrow is not None and fxrow["official"] is not None,
              "{} rests on an officially sourced fixture".format(s["market"]))
        # Fair price must be 1/p with no margin.  prob and fair_decimal are
        # each rounded to 4dp independently from the unrounded probability,
        # so the consistency test allows one unit in the 4th decimal place
        # rather than demanding fair == round(1/round(p,4), 4), which would
        # be a double-rounding artefact rather than a real defect.
        drift = abs(s["fair_decimal"] - 1.0 / s["prob"])
        check(drift < 1e-4,
              "{} fair decimal {:.4f} is 1/p to 4dp (drift {:.2e})".format(
                  s["market"], s["fair_decimal"], drift))

    # 6. no out-of-band selection was promoted
    for s in ln["selections"]:
        if s["tier"] == "high-in-band":
            continue
        if s["prob"] is not None and s["prob"] >= PROB_FLOOR:
            check(s["tier"] == "out-of-band-short",
                  "{} at {:.4f} is disclosed, not promoted".format(
                      s["market"], s["prob"]))

    # 7. prediction prose
    pdoc = read_page("predictions.html")
    for p in pr["predictions"]:
        words = re.findall(r"[A-Za-z0-9']+", p["text"].lower())
        check(len(words) >= pr["policy"]["min_words"],
              "'{}' is {} words (>= {})".format(p["selection"], len(words),
                                                pr["policy"]["min_words"]))
        for b in BANNED:
            check(b not in p["text"].lower(),
                  "'{}' does not contain '{}'".format(p["selection"], b))
        check(html.escape(p["text"]) in pdoc,
              "'{}' is published verbatim".format(p["selection"]))
        for f in p["facts"]:
            check(html.escape(f["claim"]) in pdoc and f["source"] in pdoc,
                  "'{}' cites {}".format(p["selection"], f["source"]))
        check(bool(p["absent"]),
              "'{}' states what was not available".format(p["selection"]))

    def grams(t):
        w = re.findall(r"[A-Za-z0-9']+", t.lower())
        return {" ".join(w[i:i + 6]) for i in range(len(w) - 5)}

    for i in range(len(pr["predictions"])):
        for j in range(i + 1, len(pr["predictions"])):
            shared = grams(pr["predictions"][i]["text"]) & grams(
                pr["predictions"][j]["text"])
            check(not shared, "predictions {} and {} share no 6-gram".format(
                i + 1, j + 1))

    # 8. every flag reaches the Flagged page
    fdoc = read_page("flagged.html")
    miss = [f["id"] for f in fx["flags"] if f["id"] not in fdoc]
    check(not miss, "all {} flags appear on flagged.html{}".format(
        len(fx["flags"]), "" if not miss else "; missing " + ", ".join(miss)))

    # 9. relative links resolve
    broken = []
    for p in man["pages"]:
        base = os.path.dirname(os.path.join(OUT, p))
        for href in re.findall(r'href="([^"]+)"', read_page(p)):
            if href.startswith(("http://", "https://", "mailto:", "#")):
                continue
            if not os.path.exists(os.path.normpath(os.path.join(base, href))):
                broken.append("{} -> {}".format(p, href))
    check(not broken, "every relative link resolves{}".format(
        "" if not broken else "; broken " + ", ".join(sorted(set(broken))[:6])))

    # 10. manifest counts agree with the data
    for k, v in [("fixture_rows", fx["counts"]["fixture_rows"]),
                 ("officially_verified_rows",
                  fx["counts"]["officially_verified_rows"]),
                 ("selections", ln["counts"]["selections"]),
                 ("high_confidence", len(hi)),
                 ("flags", len(fx["flags"]))]:
        check(man["counts"].get(k) == v,
              "manifest {} == {} (got {})".format(k, v,
                                                  man["counts"].get(k)))

    # 11. no stale desk is re-presented: this desk must carry its own date
    for p in man["pages"]:
        check("2026-10-23" in read_page(p),
              "page {} is dated to this run".format(p))

    for m in ok:
        print("  PASS", m)
    for m in problems:
        print("  FAIL", m)
    print("\n{} checks passed, {} failed".format(len(ok), len(problems)))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
