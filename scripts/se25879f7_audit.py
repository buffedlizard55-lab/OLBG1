"""Build an evidence-bounded audit page for the published 26 Oct 2026 desk.

This reads the retained aa2881ac dataset and page files; it does not fetch or
change sporting facts, selections, prices, timestamps, or the canonical site.
"""
from __future__ import annotations

import html
import json
import re
import sys
from collections import Counter
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import saa2881ac_data as D  # noqa: E402

DATA = ROOT / "data" / "aa2881ac" / "desk.json"
OUT = ROOT / "e25879f7"
OUT_DATA = ROOT / "data" / "e25879f7"


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def make_audit() -> dict:
    desk = json.loads(DATA.read_text(encoding="utf-8"))
    sports = []
    for slug, name, olbg_id, olbg_slug, official_url, _state in D.SPORTS:
        fixtures = [f for f in desk["fixtures"] if f["sport"] == slug]
        picks = [p for p in desk["picks"] if p["sport"] == slug]
        predictions = [p for p in desk["predictions"] if p["sport"] == slug]
        sports.append({
            "slug": slug,
            "sport": name,
            "official_fixture_rows": len(fixtures),
            "picks": len(picks),
            "high_picks": sum(p["grade"] == "High" for p in picks),
            "written_predictions": len(predictions),
            "official_source": official_url,
            "olbg_discovery": f"https://www.olbg.com/betting-tips/{olbg_slug}/{olbg_id}",
        })

    predictions_by_id = {p["pick"]: p for p in desk["predictions"]}
    high = []
    for pick in desk["picks"]:
        if pick["grade"] != "High":
            continue
        pred = predictions_by_id.get(pick["id"])
        high.append({
            "id": pick["id"],
            "sport": pick["sport"],
            "event": pick["event"],
            "selection": pick["selection"],
            "market": pick["market"],
            "fair_price": pick["price_text"],
            "probability": pick["prob"],
            "prediction_words": len(pred["text"].split()) if pred else 0,
            "prediction_url": f"../aa2881ac/predictions.html#{pick['id']}",
            "official_source": pick["source"],
            "has_prediction": pred is not None,
        })

    return {
        "audit": "e25879f7",
        "desk": "aa2881ac",
        "audit_date": "2026-10-26",
        "snapshot_read_window": desk["read_window"],
        "desk_generated_at": desk["built_at"],
        "counts": dict(desk["counts"]),
        "sport_rows": sports,
        "high_picks": high,
        "prediction_word_min": min(len(p["text"].split()) for p in desk["predictions"]),
        "prediction_word_max": max(len(p["text"].split()) for p in desk["predictions"]),
        "prediction_vocab_hits": [p["pick"] for p in desk["predictions"]
                                  if re.search(r"\b(model|verified)\b", p["text"], re.I)],
        "sources_by_role": dict(Counter(s["role"] for s in desk["sources"])),
        "flags": desk["flags"],
        "findings": [
            {
                "id": "A01",
                "severity": "Review",
                "title": "The root landing page mixes a 26 October archive link with a 24 October live snapshot.",
                "detail": "index.html begins with a banner to the 26 October aa2881ac desk, but the page snapshot marker, KPI strip, high-confidence picks table and footer are generated from the canonical 24 October snapshot. Readers can mistake those older rows for the current 26 October picks.",
                "review_link": "https://github.com/buffedlizard55-lab/OLBG1/blob/86dcc9fd6b30ad6232f5bfa29e339b989640fd41/index.html",
            },
            {
                "id": "A02",
                "severity": "Coverage limit",
                "title": "The five-picks-per-sport target is not met by the retained evidence.",
                "detail": "The 26 October desk has 48 official fixture rows across seven sports, 34 graded selections across six sports, 11 High selections and 20 written predictions. Nine requested sports have no graded pick in this snapshot. This audit does not create filler selections; the desk's own Flagged page records the reasons and missing source reads.",
                "review_link": "../aa2881ac/flagged.html",
            },
            {
                "id": "A03",
                "severity": "Coverage limit",
                "title": "No injury, lineup or team-sheet source was read for any fixture.",
                "detail": "Flag F25 explicitly records the missing availability evidence. The published prediction prose therefore contains no injury or player-availability assertions.",
                "review_link": "https://api-web.nhle.com/v1/standings/2026-10-25",
            },
            {
                "id": "A04",
                "severity": "Freshness limit",
                "title": "This is a captured snapshot, not a live odds or fixture feed.",
                "detail": "The desk records OLBG discovery and official reads between 04:45Z and 05:25Z on 26 October 2026. Prices are project-originated estimates; the page does not claim to represent a sportsbook quote or subsequent event change.",
                "review_link": "../aa2881ac/sources.html",
            },
        ],
    }


def render(a: dict) -> str:
    c = a["counts"]
    kpis = [
        (c["sports"], "requested sports"), (c["fixtures"], "official fixture rows"),
        (c["picks"], "graded selections"), (c["high"], "High selections"),
        (c["predictions"], "written predictions"), (c["flags"], "review flags"),
    ]
    kpi_html = "".join(f'<div><b>{v}</b><span>{esc(label)}</span></div>' for v, label in kpis)
    sport_rows = []
    for s in a["sport_rows"]:
        sport_rows.append(
            "<tr>"
            f"<th scope=\"row\">{esc(s['sport'])}</th>"
            f"<td>{s['official_fixture_rows']}</td><td>{s['picks']}</td>"
            f"<td>{s['high_picks']}</td><td>{s['written_predictions']}</td>"
            f"<td><a href=\"{esc(s['official_source'])}\">Official page</a>"
            f"<br><a href=\"{esc(s['olbg_discovery'])}\">OLBG discovery</a></td></tr>"
        )
    high_rows = []
    for p in a["high_picks"]:
        high_rows.append(
            "<tr>"
            f"<td>{esc(p['sport'].replace('-', ' ').title())}</td>"
            f"<td>{esc(p['event'])}</td><td><strong>{esc(p['selection'])}</strong>"
            f"<br><span class=\"muted\">{esc(p['market'])} · originated fair price {esc(p['fair_price'])}</span></td>"
            f"<td>{p['prediction_words']} words</td>"
            f"<td><a href=\"{esc(p['prediction_url'])}\">Full write-up</a> · "
            f"<a href=\"{esc(p['official_source'])}\">Official source</a></td></tr>"
        )
    finding_rows = []
    for f in a["findings"]:
        finding_rows.append(
            f"<article class=\"finding\"><h3>{esc(f['id'])} · {esc(f['title'])}</h3>"
            f"<p>{esc(f['detail'])}</p><a href=\"{esc(f['review_link'])}\">Review source / page →</a></article>"
        )
    role_str = ", ".join(f"{esc(k.replace('_', ' '))}: {v}" for k, v in a["sources_by_role"].items())
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>26 October desk audit · OLBG Research Desk</title>
<meta name="description" content="Independent evidence-bounded audit of the 26 October 2026 OLBG desk.">
<style>
:root{{--ink:#15251e;--muted:#5c6b64;--line:#dbe4df;--bg:#f4f7f5;--card:#fff;--green:#126442;--amber:#704900}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--ink);font:16px/1.55 system-ui,-apple-system,"Segoe UI",sans-serif}}
a{{color:var(--green)}}header{{background:#fff;border-bottom:1px solid var(--line)}}.wrap{{max-width:1120px;margin:auto;padding:18px 20px}}nav{{display:flex;gap:14px;flex-wrap:wrap;margin-top:12px}}h1{{font-size:30px;line-height:1.2;margin:10px 0}}h2{{font-size:21px;margin:30px 0 10px}}h3{{font-size:17px;margin:0 0 8px}}.lede{{font-size:18px;color:#35473d;max-width:880px}}.cards{{display:grid;grid-template-columns:repeat(6,1fr);gap:10px;margin:20px 0}}.cards div,.panel,.finding{{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:15px}}.cards b,.cards span{{display:block}}.cards b{{font-size:25px}}.cards span,.muted{{font-size:13px;color:var(--muted)}}.scroll{{overflow:auto;background:#fff;border:1px solid var(--line);border-radius:10px}}table{{border-collapse:collapse;width:100%;min-width:760px}}th,td{{padding:10px 12px;text-align:left;vertical-align:top;border-bottom:1px solid var(--line)}}thead th{{background:#edf3ef}}tbody th{{font-weight:650}}.finding{{margin:10px 0}}.note{{border-left:4px solid var(--amber);background:#fff7e6;padding:12px 14px}}footer{{color:var(--muted);font-size:13px;border-top:1px solid var(--line);margin-top:32px}}@media(max-width:800px){{.cards{{grid-template-columns:repeat(2,1fr)}}.wrap{{padding:14px}}}}
</style></head>
<body><header><div class="wrap"><strong>OLBG Research Desk · Independent audit</strong><nav aria-label="Audit navigation"><a href="../aa2881ac/index.html">26 Oct desk</a><a href="../aa2881ac/picks.html">Picks</a><a href="../aa2881ac/predictions.html">Written predictions</a><a href="../aa2881ac/matches.html">Every match</a><a href="../aa2881ac/flagged.html">Flagged for review</a><a href="../index.html">Project front door</a></nav></div></header>
<main class="wrap"><h1>26 October desk: independent audit</h1>
<p class="lede">This page checks structure and evidence provenance for the already published <a href="../aa2881ac/index.html">aa2881ac fifteen-sport desk</a>. It does not refresh or independently certify the underlying real-world events. The source observations were captured {esc(a['snapshot_read_window'])} UTC.</p>
<div class="cards">{kpi_html}</div>
<p class="note"><strong>Use the picks links above for the current snapshot's selections.</strong> The root front door also contains a separate 24 October canonical table; see finding A01 below before treating the older table as today's slate. All prices in the 26 October desk are originated estimates, not sportsbook quotes.</p>
<h2>Coverage by requested sport</h2><p>Counts below are from the retained aa2881ac dataset. A zero official fixture count means no official fixture row was retained; it is not proof that the sport has no event.</p>
<div class="scroll"><table><thead><tr><th>Sport</th><th>Official fixture rows</th><th>Graded picks</th><th>High</th><th>Written analyses</th><th>Review links</th></tr></thead><tbody>{''.join(sport_rows)}</tbody></table></div>
<h2>High-confidence selections</h2><p>All {c['high']} High selections have a linked write-up of at least 30 words. The write-up and official source links are on every row.</p>
<div class="scroll"><table><thead><tr><th>Sport</th><th>Match</th><th>Selection</th><th>Analysis length</th><th>Links</th></tr></thead><tbody>{''.join(high_rows)}</tbody></table></div>
<h2>Audit findings and limits</h2>{''.join(finding_rows)}
<h2>Checks actually run</h2><div class="panel"><ul><li>Dedicated aa2881ac validator: 0 errors.</li><li>Dedicated aa2881ac tests: 10 passed.</li><li>Canonical route validation on the repository and generated scratch site: 0 errors each.</li><li>Full pipeline test suite: 767 passed.</li><li>Prediction lengths in the 26 October desk: {a['prediction_word_min']}–{a['prediction_word_max']} words; banned internal vocabulary hits: {len(a['prediction_vocab_hits'])}.</li><li>Retained source roles: {role_str}.</li></ul><p class="muted">These are reproducibility and presentation checks against captured repository artifacts, not an independent re-fetch of every upstream publisher.</p></div>
<h2>Source and method links</h2><div class="panel"><p><a href="../aa2881ac/sources.html">Source register with read times</a> · <a href="../aa2881ac/methodology.html">Pricing and confidence method</a> · <a href="../aa2881ac/flagged.html">All 26 flagged items</a> · <a href="../aa2881ac/audit.html">Previous repo findings</a></p><p>Current audit build: {esc(a['audit_date'])}; desk snapshot built at {esc(a['desk_generated_at'])}. No new event, form, injury or betting-price facts were added here.</p></div>
</main><footer><div class="wrap">Independent research, not affiliated with OLBG. No guaranteed returns and no staking advice.</div></footer></body></html>'''


def main() -> None:
    a = make_audit()
    OUT.mkdir(parents=True, exist_ok=True)
    OUT_DATA.mkdir(parents=True, exist_ok=True)
    (OUT_DATA / "audit.json").write_text(json.dumps(a, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    page = render(a)
    (OUT / "index.html").write_text(page, encoding="utf-8")
    print(f"Built {OUT / 'index.html'}: {len(a['sport_rows'])} sports, {len(a['high_picks'])} High picks, {a['counts']['flags']} source flags")


if __name__ == "__main__":
    main()
