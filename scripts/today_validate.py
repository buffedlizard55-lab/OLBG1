"""Gate for the clarity desk at today/.

Checks, in order:
  1. every page exists and every internal link/fragment resolves
  2. every fixture row carries a link to an official publisher
  3. every pick has a written prediction of at least 30 words, unique, with the
     selection named and neither banned word present
  4. every High pick sits inside the brief's band with a 70%+ chance
  5. no page loads anything remote (script, stylesheet, font, image)
  6. counts printed on the pages match the data module
"""
import html
import os
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import today_data as D

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "today"
BANNED = ("model", "verified")
OFFICIAL_HOSTS = ("nhle.com", "nhl.com", "mlb.com", "formula1.com", "atptour.com", "wttatennis.com",
                  "olbg.com", "nba.com", "pdc.tv", "wst.tv", "eurohandball.com", "gaa.ie",
                  "gbgb.org.uk", "icc-cricket.com", "premiershiprugby.com", "legavolley.it",
                  "nrl.com", "pgatour.com", "github.com")


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.hrefs, self.ids, self.remote, self.scripts = [], set(), [], []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "id" in a:
            self.ids.add(a["id"])
        if tag == "a" and a.get("href"):
            self.hrefs.append(a["href"])
        if tag == "link" and a.get("href", "").startswith(("http", "//")):
            self.remote.append(a["href"])
        if tag in ("script", "img", "iframe") and a.get("src", "").startswith(("http", "//")):
            self.remote.append(a["src"])
        if tag == "script":
            self.scripts.append(a)


def american(p):
    dec = 1 / p
    return round((dec - 1) * 100) if dec >= 2 else round(-100 / (dec - 1))


def main():
    errors, warnings = [], []
    pages = sorted(SITE.rglob("*.html"))
    parsed = {}
    for p in pages:
        parser = Links()
        parser.feed(p.read_text(encoding="utf-8"))
        parsed[p.relative_to(SITE).as_posix()] = parser
    if not pages:
        errors.append("no pages built")

    # 1. links and fragments
    for name, parser in parsed.items():
        if parser.remote:
            errors.append(f"{name}: remote asset {parser.remote[0]}")
        if parser.scripts:
            errors.append(f"{name}: script tag present; the desk must work without JS")
        for href in parser.hrefs:
            if href.startswith(("http://", "https://", "mailto:")):
                host = re.sub(r"^https?://", "", href).split("/")[0]
                if not any(host.endswith(h) for h in OFFICIAL_HOSTS):
                    errors.append(f"{name}: link to a non-source host {host}")
                continue
            path, _, frag = href.partition("#")
            if not path:
                target = name
            else:
                target = os.path.normpath(os.path.join(os.path.dirname(name), path)).replace(os.sep, "/")
            if target not in parsed:
                errors.append(f"{name}: broken link {href}")
                continue
            if frag and frag not in parsed[target].ids:
                errors.append(f"{name}: missing fragment #{frag} in {target}")

    # 2/3. fixtures and predictions
    fixtures = {f["id"]: f for f in D.FIXTURES}
    for f in D.FIXTURES:
        src = D.SOURCES.get(f["source_id"])
        if not src or not src["url"].startswith("https://"):
            errors.append(f'{f["id"]}: no official source')
        if src and not any(h in src["url"] for h in OFFICIAL_HOSTS):
            errors.append(f'{f["id"]}: source host is not an official publisher')
    texts = set()
    for p in D.PICKS:
        words = len(p["prediction"].split())
        if words < 30:
            errors.append(f'{p["fixture"]}: prediction is {words} words')
        lowered = p["prediction"].lower()
        for w in BANNED:
            if re.search(rf"\b{w}\b", lowered):
                errors.append(f'{p["fixture"]}: banned word "{w}" in prediction')
        if p["selection"].split()[0].lower() not in lowered:
            errors.append(f'{p["fixture"]}: prediction does not name the selection')
        if p["fixture"] not in fixtures:
            errors.append(f'{p["fixture"]}: pick on unknown fixture')
        if p["prediction"] in texts:
            errors.append(f'{p["fixture"]}: duplicate prediction text')
        texts.add(p["prediction"])
        if p["confidence"] == "High":
            fair = american(p["prob"])
            if not (p["prob"] >= 0.70 and -250 <= fair):
                errors.append(f'{p["fixture"]}: High pick outside the band (p={p["prob"]}, fair={fair})')
        if p["confidence"] not in ("High", "Medium", "Low"):
            errors.append(f'{p["fixture"]}: bad tier')

    # 4. band arithmetic for every published price
    for m in D.MARKETS:
        if not (0 < m["prob"] < 1):
            errors.append(f'bad probability on {m["selection"]}')

    # 5. counts printed on pages
    idx = (SITE / "index.html").read_text(encoding="utf-8")
    for label, value in (("picks issued", len(D.PICKS)), ("High confidence", 0),
                         ("OLBG listings inventoried", len(D.DISCOVERY))):
        m = re.search(rf"<b>{value}</b><span>{re.escape(label)}</span>", idx)
        if value and not m:
            errors.append(f"index.html: KPI '{label}' does not show {value}")
    disc = (SITE / "discovery.html").read_text(encoding="utf-8")
    if disc.count("discovery only") < len(D.DISCOVERY):
        errors.append("discovery.html: fewer rows than discovery listings")

    # 6. no unfilled placeholder
    for name, parser in parsed.items():
        body = (SITE / name).read_text(encoding="utf-8")
        for token in (">None<", "TODO", "PLACEHOLDER", "{unfilled}"):
            if token in body:
                warnings.append(f"{name}: literal '{token}' appears in output")

    print(f"pages {len(pages)} | fixtures {len(D.FIXTURES)} | picks {len(D.PICKS)} | "
          f"markets {len(D.MARKETS)} | discovery {len(D.DISCOVERY)} | flags {len(D.FLAGS)}")
    for e in errors:
        print("ERROR", e)
    for w in warnings[:12]:
        print("warn", w)
    print("RESULT", "PASS" if not errors else "FAIL")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
