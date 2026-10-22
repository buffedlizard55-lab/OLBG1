/* OLBG Independent Desk - small progressive enhancement.
   The site is complete without this file: tables, links and prices are all in the HTML.
   This only adds filtering on the all-matches page and a "show/hide all" control. */

(function () {
  "use strict";

  function ready(fn) {
    if (document.readyState !== "loading") fn();
    else document.addEventListener("DOMContentLoaded", fn);
  }

  ready(function () {
    var table = document.querySelector("table.grid");
    var sport = document.getElementById("f-sport");
    var conf = document.getElementById("f-conf");
    var query = document.getElementById("f-q");
    var count = document.getElementById("f-count");

    if (table && sport && conf) {
      var rows = Array.prototype.slice.call(table.querySelectorAll("tbody tr"));
      var total = rows.length;

      var apply = function () {
        var s = sport.value;
        var c = conf.value;
        var q = (query && query.value ? query.value : "").toLowerCase().trim();
        var shown = 0;

        rows.forEach(function (row) {
          var text = row.textContent.toLowerCase();
          var rowSport = row.getAttribute("data-sport") || "";
          var rowConf = row.getAttribute("data-conf") || "";
          var ok = true;
          if (s && rowSport !== s) ok = false;
          if (ok && c && rowConf !== c) ok = false;
          if (ok && q && text.indexOf(q) === -1) ok = false;
          row.style.display = ok ? "" : "none";
          if (ok) shown += 1;
        });

        if (count) count.textContent = shown + " of " + total + " rows shown";
      };

      [sport, conf, query].forEach(function (el) {
        if (el) el.addEventListener("input", apply);
      });
      apply();
    }

    var sheets = document.querySelectorAll("details.mkt");
    if (sheets.length > 12) {
      var bar = document.createElement("p");
      bar.className = "sub";
      var btn = document.createElement("button");
      btn.type = "button";
      btn.textContent = "Expand all market sheets";
      btn.className = "tag lo";
      btn.style.cursor = "pointer";
      var open = false;
      btn.addEventListener("click", function () {
        open = !open;
        Array.prototype.forEach.call(sheets, function (d) { d.open = open; });
        btn.textContent = open ? "Collapse all market sheets" : "Expand all market sheets";
      });
      bar.appendChild(btn);
      sheets[0].parentNode.insertBefore(bar, sheets[0]);
    }
  });
})();
