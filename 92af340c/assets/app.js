// Interactive progressive enhancement: composable filters (confidence + sport + text search),
// live odds format toggle (Bookmaker 5% Vig / Vig-Free Fair / US Moneyline), and market drawer controls.
(function () {
  "use strict";

  function ready(fn) {
    if (document.readyState !== "loading") fn();
    else document.addEventListener("DOMContentLoaded", fn);
  }

  ready(function () {
    var activeConf = "all";
    var activeSport = "all";
    var searchInput = document.getElementById("pick-search");
    var sportSelect = document.getElementById("sport-filter");
    var confButtons = document.querySelectorAll("[data-filter]");
    var filterableRows = document.querySelectorAll("[data-conf]");
    var visibleCounter = document.querySelector("[data-visible-count]");

    function applyFilters() {
      var q = searchInput ? searchInput.value.trim().toLowerCase() : "";
      var shown = 0;
      filterableRows.forEach(function (el) {
        var cOk = activeConf === "all" || el.getAttribute("data-conf") === activeConf;
        var sOk = activeSport === "all" || el.getAttribute("data-sport") === activeSport;
        var qOk = !q || el.textContent.toLowerCase().indexOf(q) !== -1;
        var visible = cOk && sOk && qOk;
        el.style.display = visible ? "" : "none";
        if (visible) shown++;
      });
      if (visibleCounter) visibleCounter.textContent = String(shown);
    }

    if (confButtons.length) {
      confButtons.forEach(function (btn) {
        btn.addEventListener("click", function () {
          activeConf = btn.getAttribute("data-filter") || "all";
          confButtons.forEach(function (b) {
            b.classList.remove("is-active");
            b.setAttribute("aria-pressed", "false");
          });
          btn.classList.add("is-active");
          btn.setAttribute("aria-pressed", "true");
          applyFilters();
        });
      });
    }

    if (sportSelect) {
      sportSelect.addEventListener("change", function () {
        activeSport = sportSelect.value || "all";
        applyFilters();
      });
    }

    if (searchInput) {
      searchInput.addEventListener("input", applyFilters);
    }

    // Live Odds Format Switcher (dec = 5% overround decimal, fair = vig-free decimal, us = American moneyline)
    var fmtButtons = document.querySelectorAll("[data-odds-fmt]");
    if (fmtButtons.length) {
      fmtButtons.forEach(function (btn) {
        btn.addEventListener("click", function () {
          var mode = btn.getAttribute("data-odds-fmt") || "dec";
          fmtButtons.forEach(function (b) {
            b.classList.remove("is-active");
            b.setAttribute("aria-pressed", "false");
          });
          btn.classList.add("is-active");
          btn.setAttribute("aria-pressed", "true");
          document.querySelectorAll("[data-dec]").forEach(function (span) {
            var val = span.getAttribute("data-" + mode);
            if (val) span.textContent = val;
          });
        });
      });
    }

    // Open / Collapse All Market Drawers
    var openAll = document.getElementById("open-all");
    if (openAll) {
      openAll.addEventListener("click", function (e) {
        e.preventDefault();
        var nextOpen = openAll.getAttribute("data-state") !== "open";
        document.querySelectorAll("details.markets").forEach(function (d) { d.open = nextOpen; });
        openAll.setAttribute("data-state", nextOpen ? "open" : "closed");
        openAll.textContent = nextOpen ? "Collapse all markets" : "Expand all markets";
      });
    }
  });
})();
