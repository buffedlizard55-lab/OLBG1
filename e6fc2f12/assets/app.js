/* Session e6fc2f12-olbg1 — local-only helpers. No network, no storage, no tracking. */
(function () {
  "use strict";

  function apply(tableId, sportId, tierId, countId) {
    var table = document.getElementById(tableId);
    if (!table) return;
    var sport = document.getElementById(sportId);
    var tier = document.getElementById(tierId);
    var count = document.getElementById(countId);

    function run() {
      var s = sport ? sport.value : "";
      var t = tier ? tier.value : "";
      var shown = 0;
      var rows = table.tBodies[0].rows;
      for (var i = 0; i < rows.length; i++) {
        var row = rows[i];
        var okSport = !s || row.getAttribute("data-sport") === s;
        var okTier = !t || row.getAttribute("data-tier") === t;
        var show = okSport && okTier;
        row.style.display = show ? "" : "none";
        if (show) shown++;
      }
      if (count) count.textContent = shown + " of " + rows.length + " rows shown";
    }

    if (sport) sport.addEventListener("change", run);
    if (tier) tier.addEventListener("change", run);
    run();
  }

  apply("marketTable", "sportFilter", "tierFilter", "rowCount");
})();
