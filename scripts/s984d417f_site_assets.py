#!/usr/bin/env python3
"""
s984d417f_site_assets.py — Clean, high-contrast CSS and interactive vanilla JS
(odds format switcher, dark/light theme toggle, live search + multi-facet filtering,
sortable columns, and expandable market drawers) for /984d417f/.
"""
from __future__ import annotations

SITE_CSS = """\
:root {
  --bg: #f6f8fb;
  --surface: #ffffff;
  --surface-alt: #f0f4f9;
  --border: #d9e2ec;
  --border-strong: #bcccdc;
  --text: #102a43;
  --text-muted: #486581;
  --brand: #0b4f6c;
  --brand-strong: #073b52;
  --brand-soft: #e6f4f8;
  --accent: #0f766e;
  --high-bg: #dcfce7;
  --high-fg: #14532d;
  --high-bd: #86efac;
  --med-bg: #dbeafe;
  --med-fg: #1e3a8a;
  --med-bd: #93c5fd;
  --low-bg: #f1f5f9;
  --low-fg: #334155;
  --low-bd: #cbd5e1;
  --warn-bg: #fef3c7;
  --warn-fg: #78350f;
  --warn-bd: #fcd34d;
  --err-bg: #fee2e2;
  --err-fg: #7f1d1d;
  --err-bd: #fca5a5;
  --shadow: 0 1px 3px rgba(16, 42, 67, 0.07), 0 4px 12px rgba(16, 42, 67, 0.04);
  --radius: 10px;
}

[data-theme="dark"] {
  --bg: #0b1320;
  --surface: #111c2d;
  --surface-alt: #17263c;
  --border: #243752;
  --border-strong: #354f73;
  --text: #e6eef8;
  --text-muted: #9fb3c8;
  --brand: #38bdf8;
  --brand-strong: #7dd3fc;
  --brand-soft: #132c44;
  --accent: #2dd4bf;
  --high-bg: #063b27;
  --high-fg: #86efac;
  --high-bd: #15803d;
  --med-bg: #122b54;
  --med-fg: #93c5fd;
  --med-bd: #2563eb;
  --low-bg: #1e293b;
  --low-fg: #cbd5e1;
  --low-bd: #475569;
  --warn-bg: #422906;
  --warn-fg: #fde68a;
  --warn-bd: #b45309;
  --err-bg: #451217;
  --err-fg: #fca5a5;
  --err-bd: #b91c1c;
  --shadow: 0 2px 10px rgba(0, 0, 0, 0.35);
}

* { box-sizing: border-box; }
html { scroll-behavior: smooth; }
body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Inter, "Helvetica Neue", Arial, sans-serif;
  background: var(--bg);
  color: var(--text);
  line-height: 1.55;
  font-size: 14.5px;
}

a { color: var(--brand); text-decoration: none; }
a:hover { text-decoration: underline; color: var(--brand-strong); }

.topbar {
  position: sticky;
  top: 0;
  z-index: 50;
  background: var(--surface);
  border-bottom: 1px solid var(--border);
  box-shadow: 0 1px 4px rgba(16, 42, 67, 0.05);
}
.topbar-inner {
  max-width: 1440px;
  margin: 0 auto;
  padding: 0.65rem 1.25rem;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
}
.brand {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  font-weight: 800;
  font-size: 1.02rem;
  color: var(--text);
  text-decoration: none;
}
.brand-badge {
  background: var(--brand);
  color: #fff;
  padding: 0.2rem 0.5rem;
  border-radius: 6px;
  font-size: 0.75rem;
  letter-spacing: 0.04em;
  font-weight: 800;
}
[data-theme="dark"] .brand-badge { color: #07192b; }

.nav-links {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.3rem;
}
.nav-links a {
  padding: 0.38rem 0.68rem;
  border-radius: 6px;
  font-weight: 600;
  font-size: 0.86rem;
  color: var(--text-muted);
  text-decoration: none;
}
.nav-links a:hover, .nav-links a.active {
  background: var(--brand-soft);
  color: var(--brand);
}
.nav-links a.flag-nav {
  border: 1px solid var(--warn-bd);
  background: var(--warn-bg);
  color: var(--warn-fg);
}

.utility-controls {
  display: flex;
  align-items: center;
  gap: 0.45rem;
}
.btn-ctrl, select.ctrl-select {
  background: var(--surface-alt);
  color: var(--text);
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 0.34rem 0.6rem;
  font-size: 0.8rem;
  font-weight: 600;
  cursor: pointer;
}
.btn-ctrl:hover { border-color: var(--brand); }

.sport-ribbon {
  background: var(--surface-alt);
  border-bottom: 1px solid var(--border);
}
.sport-ribbon-inner {
  max-width: 1440px;
  margin: 0 auto;
  padding: 0.42rem 1.25rem;
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
  align-items: center;
}
.sport-pill {
  font-size: 0.77rem;
  font-weight: 600;
  padding: 0.2rem 0.52rem;
  border-radius: 999px;
  background: var(--surface);
  border: 1px solid var(--border);
  color: var(--text-muted);
  text-decoration: none;
  white-space: nowrap;
}
.sport-pill:hover, .sport-pill.active {
  background: var(--brand);
  color: #fff;
  border-color: var(--brand);
  text-decoration: none;
}
[data-theme="dark"] .sport-pill:hover,
[data-theme="dark"] .sport-pill.active { color: #07192b; }

.container {
  max-width: 1440px;
  margin: 0 auto;
  padding: 1.5rem 1.25rem 3.5rem;
}

.hero {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 1.45rem 1.6rem;
  box-shadow: var(--shadow);
  margin-bottom: 1.25rem;
}
.eyebrow {
  display: inline-block;
  font-size: 0.74rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.07em;
  color: var(--accent);
  background: var(--brand-soft);
  padding: 0.2rem 0.55rem;
  border-radius: 999px;
  margin-bottom: 0.5rem;
}
.hero h1 {
  margin: 0 0 0.45rem;
  font-size: 1.68rem;
  line-height: 1.22;
  letter-spacing: -0.015em;
}
.hero p {
  margin: 0.3rem 0 0;
  color: var(--text-muted);
  max-width: 980px;
}

.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(175px, 1fr));
  gap: 0.85rem;
  margin-bottom: 1.4rem;
}
.kpi-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 0.95rem 1.05rem;
  box-shadow: var(--shadow);
}
.kpi-val {
  font-size: 1.52rem;
  font-weight: 800;
  line-height: 1.15;
  color: var(--brand);
}
.kpi-lbl {
  font-size: 0.78rem;
  font-weight: 700;
  margin-top: 0.25rem;
  color: var(--text);
}
.kpi-sub {
  font-size: 0.74rem;
  color: var(--text-muted);
  margin-top: 0.15rem;
}

.section-head {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  align-items: baseline;
  gap: 0.6rem;
  margin: 1.75rem 0 0.8rem;
}
.section-head h2 {
  margin: 0;
  font-size: 1.22rem;
  letter-spacing: -0.01em;
}
.section-head .meta {
  font-size: 0.82rem;
  color: var(--text-muted);
}

.sport-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(265px, 1fr));
  gap: 0.85rem;
}
.sport-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 1rem 1.1rem;
  box-shadow: var(--shadow);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  gap: 0.65rem;
}
.sport-card:hover { border-color: var(--brand); }
.sport-card-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 0.5rem;
}
.sport-card h3 {
  margin: 0;
  font-size: 1.02rem;
}
.count-chip {
  font-size: 0.74rem;
  font-weight: 700;
  padding: 0.16rem 0.5rem;
  border-radius: 999px;
  background: var(--brand-soft);
  color: var(--brand);
}
.sport-card .comps {
  font-size: 0.8rem;
  color: var(--text-muted);
}
.sport-card-links {
  display: flex;
  flex-wrap: wrap;
  gap: 0.45rem;
  font-size: 0.77rem;
  padding-top: 0.45rem;
  border-top: 1px solid var(--border);
}

.filter-bar {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 0.8rem 1rem;
  margin-bottom: 0.85rem;
  display: flex;
  flex-wrap: wrap;
  gap: 0.6rem;
  align-items: center;
}
.filter-bar input[type="search"], .filter-bar select {
  background: var(--surface-alt);
  color: var(--text);
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 0.42rem 0.68rem;
  font-size: 0.84rem;
}
.filter-bar input[type="search"] { min-width: 240px; flex: 1 1 240px; }
.filter-count {
  font-size: 0.8rem;
  font-weight: 700;
  color: var(--text-muted);
  margin-left: auto;
}

.table-wrap {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  overflow-x: auto;
}
table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.83rem;
}
thead th {
  background: var(--surface-alt);
  color: var(--text);
  font-weight: 700;
  text-align: left;
  padding: 0.68rem 0.72rem;
  border-bottom: 2px solid var(--border);
  white-space: nowrap;
  user-select: none;
}
thead th[data-sort] { cursor: pointer; }
thead th[data-sort]:hover { color: var(--brand); }
tbody td {
  padding: 0.62rem 0.72rem;
  border-bottom: 1px solid var(--border);
  vertical-align: top;
}
tbody tr.data-row:hover { background: var(--surface-alt); }
tbody tr.flagged-row { background: rgba(245, 158, 11, 0.045); }

.badge {
  display: inline-block;
  font-size: 0.71rem;
  font-weight: 800;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  padding: 0.16rem 0.46rem;
  border-radius: 5px;
  border: 1px solid transparent;
  white-space: nowrap;
}
.badge-high { background: var(--high-bg); color: var(--high-fg); border-color: var(--high-bd); }
.badge-medium { background: var(--med-bg); color: var(--med-fg); border-color: var(--med-bd); }
.badge-low { background: var(--low-bg); color: var(--low-fg); border-color: var(--low-bd); }
.badge-warn { background: var(--warn-bg); color: var(--warn-fg); border-color: var(--warn-bd); }
.badge-err { background: var(--err-bg); color: var(--err-fg); border-color: var(--err-bd); }

.blank-cell {
  display: inline-block;
  font-size: 0.73rem;
  font-weight: 700;
  padding: 0.12rem 0.42rem;
  border-radius: 4px;
  background: var(--warn-bg);
  color: var(--warn-fg);
  border: 1px dashed var(--warn-bd);
}

.src-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.3rem;
}
.src-pill {
  display: inline-block;
  font-size: 0.73rem;
  font-weight: 600;
  padding: 0.14rem 0.44rem;
  border-radius: 4px;
  background: var(--brand-soft);
  color: var(--brand);
  border: 1px solid var(--border);
  white-space: nowrap;
}
.src-pill.olbg-pill {
  background: var(--surface-alt);
  color: var(--text-muted);
}

.pred-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 1rem;
}
@media (max-width: 640px) {
  .pred-grid { grid-template-columns: 1fr; }
}
.pred-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 1.15rem 1.25rem;
  box-shadow: var(--shadow);
  display: flex;
  flex-direction: column;
  gap: 0.65rem;
}
.pred-card h3 {
  margin: 0;
  font-size: 1.03rem;
  line-height: 1.3;
}
.pred-pick-box {
  background: var(--brand-soft);
  border-left: 3px solid var(--brand);
  padding: 0.5rem 0.7rem;
  border-radius: 0 6px 6px 0;
  font-size: 0.81rem;
  font-weight: 700;
}
.pred-prose {
  margin: 0;
  font-size: 0.89rem;
  line-height: 1.62;
  color: var(--text);
}
.pred-meta {
  font-size: 0.77rem;
  color: var(--text-muted);
  display: grid;
  gap: 0.2rem;
  padding-top: 0.45rem;
  border-top: 1px solid var(--border);
}

.callout-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(340px, 1fr));
  gap: 0.9rem;
}
.callout {
  background: var(--surface);
  border: 1px solid var(--border);
  border-left: 4px solid var(--brand);
  border-radius: var(--radius);
  padding: 0.95rem 1.1rem;
  box-shadow: var(--shadow);
}
.callout.warn { border-left-color: #d97706; }
.callout.err { border-left-color: #dc2626; }
.callout h3 { margin: 0 0 0.35rem; font-size: 0.96rem; }
.callout p { margin: 0.25rem 0; font-size: 0.83rem; color: var(--text-muted); }

details.runner-drawer summary {
  cursor: pointer;
  font-weight: 700;
  color: var(--brand);
  font-size: 0.79rem;
}
.mono { font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; font-size: 0.79rem; }

footer {
  border-top: 1px solid var(--border);
  background: var(--surface);
  padding: 1.25rem;
  color: var(--text-muted);
  font-size: 0.8rem;
}
footer .footer-inner {
  max-width: 1440px;
  margin: 0 auto;
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  gap: 0.75rem;
}
"""

SITE_JS = """\
(function () {
  const root = document.documentElement;
  const savedTheme = localStorage.getItem("olbg984_theme");
  if (savedTheme === "dark") root.setAttribute("data-theme", "dark");

  function applyOddsFormat(fmt) {
    localStorage.setItem("olbg984_odds", fmt);
    document.querySelectorAll("[data-dec]").forEach(function (el) {
      const dec = parseFloat(el.getAttribute("data-dec"));
      const amer = el.getAttribute("data-amer") || "";
      const prob = parseFloat(el.getAttribute("data-prob") || "0");
      if (!dec || isNaN(dec)) return;
      if (fmt === "american" && amer) {
        el.textContent = amer;
      } else if (fmt === "prob" && prob > 0) {
        el.textContent = (prob * 100).toFixed(1) + "%";
      } else {
        el.textContent = dec.toFixed(2);
      }
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    const themeBtn = document.getElementById("theme-toggle");
    if (themeBtn) {
      themeBtn.addEventListener("click", function () {
        const next = root.getAttribute("data-theme") === "dark" ? "light" : "dark";
        if (next === "dark") root.setAttribute("data-theme", "dark");
        else root.removeAttribute("data-theme");
        localStorage.setItem("olbg984_theme", next);
      });
    }

    const oddsSel = document.getElementById("odds-format");
    const savedOdds = localStorage.getItem("olbg984_odds") || "decimal";
    if (oddsSel) {
      oddsSel.value = savedOdds;
      oddsSel.addEventListener("change", function () { applyOddsFormat(oddsSel.value); });
    }
    applyOddsFormat(savedOdds);

    // Interactive filtering on any [data-filter-table]
    document.querySelectorAll("[data-filter-bar]").forEach(function (bar) {
      const targetId = bar.getAttribute("data-filter-bar");
      const container = document.getElementById(targetId);
      if (!container) return;
      const items = Array.from(container.querySelectorAll("[data-filter-item]"));
      const qInput = bar.querySelector("[data-f-q]");
      const spSel = bar.querySelector("[data-f-sport]");
      const cfSel = bar.querySelector("[data-f-conf]");
      const stSel = bar.querySelector("[data-f-status]");
      const counter = bar.querySelector("[data-f-count]");

      function refresh() {
        const q = (qInput ? qInput.value : "").trim().toLowerCase();
        const sp = spSel ? spSel.value : "";
        const cf = cfSel ? cfSel.value : "";
        const st = stSel ? stSel.value : "";
        let shown = 0;
        items.forEach(function (el) {
          const okQ = !q || (el.textContent || "").toLowerCase().indexOf(q) !== -1;
          const okSp = !sp || el.getAttribute("data-sport") === sp;
          const okCf = !cf || el.getAttribute("data-conf") === cf;
          const okSt = !st || el.getAttribute("data-status") === st;
          const vis = okQ && okSp && okCf && okSt;
          el.style.display = vis ? "" : "none";
          if (vis) shown += 1;
        });
        if (counter) counter.textContent = shown + " / " + items.length + " shown";
      }

      [qInput, spSel, cfSel, stSel].forEach(function (ctrl) {
        if (!ctrl) return;
        ctrl.addEventListener("input", refresh);
        ctrl.addEventListener("change", refresh);
      });
      refresh();
    });

    // Click-to-sort columns on tables
    document.querySelectorAll("table[data-sortable]").forEach(function (tbl) {
      const headers = tbl.querySelectorAll("thead th[data-sort]");
      headers.forEach(function (th, idx) {
        let asc = true;
        th.addEventListener("click", function () {
          const tbody = tbl.querySelector("tbody");
          const rows = Array.from(tbody.querySelectorAll("tr.data-row"));
          const mode = th.getAttribute("data-sort");
          rows.sort(function (a, b) {
            const av = (a.children[idx] ? a.children[idx].getAttribute("data-val") || a.children[idx].textContent : "").trim();
            const bv = (b.children[idx] ? b.children[idx].getAttribute("data-val") || b.children[idx].textContent : "").trim();
            if (mode === "num") {
              const an = parseFloat(av) || -999999;
              const bn = parseFloat(bv) || -999999;
              return asc ? an - bn : bn - an;
            }
            return asc ? av.localeCompare(bv) : bv.localeCompare(av);
          });
          asc = !asc;
          rows.forEach(function (r) { tbody.appendChild(r); });
        });
      });
    });
  });
})();
"""
