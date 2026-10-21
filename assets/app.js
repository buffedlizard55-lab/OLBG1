// Small progressive-enhancement helpers for the dashboard. No framework, no network calls.
(function () {
  "use strict";

  function ready(fn) {
    if (document.readyState !== "loading") fn();
    else document.addEventListener("DOMContentLoaded", fn);
  }

  ready(function () {
    // --- confidence filters -------------------------------------------------
    var filters = document.querySelectorAll("[data-filter]");
    var rows = document.querySelectorAll("[data-conf]");
    if (filters.length && rows.length) {
      filters.forEach(function (btn) {
        btn.addEventListener("click", function () {
          var want = btn.getAttribute("data-filter");
          filters.forEach(function (b) { b.classList.remove("is-active"); b.setAttribute("aria-pressed", "false"); });
          btn.classList.add("is-active");
          btn.setAttribute("aria-pressed", "true");
          rows.forEach(function (r) {
            var show = want === "all" || r.getAttribute("data-conf") === want;
            r.style.display = show ? "" : "none";
          });
          var t = document.querySelector("[data-visible-count]");
          if (t) {
            var shown = 0;
            rows.forEach(function (r) { if (r.style.display !== "none") shown++; });
            t.textContent = shown;
          }
        });
      });
    }

    // --- free-text search over the picks table -----------------------------
    var search = document.getElementById("pick-search");
    if (search && rows.length) {
      search.addEventListener("input", function () {
        var q = search.value.trim().toLowerCase();
        rows.forEach(function (r) {
          var hit = !q || r.textContent.toLowerCase().indexOf(q) !== -1;
          r.style.display = hit ? "" : "none";
        });
      });
    }

    // --- open/close all market drawers -------------------------------------
    var openAll = document.getElementById("open-all");
    if (openAll) {
      openAll.addEventListener("click", function (e) {
        e.preventDefault();
        var open = openAll.getAttribute("data-state") !== "open";
        document.querySelectorAll("details.markets").forEach(function (d) { d.open = open; });
        openAll.setAttribute("data-state", open ? "open" : "closed");
        openAll.textContent = open ? "Collapse all markets" : "Expand all markets";
      });
    }
  });
})();
