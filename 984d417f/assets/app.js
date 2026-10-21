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
