(function () {
  var q = document.getElementById("q"), cf = document.getElementById("cf"), count = document.getElementById("count");
  if (!q) return;
  var rows = Array.prototype.slice.call(document.querySelectorAll("tbody tr[data-conf]"));
  function apply() {
    var t = q.value.trim().toLowerCase(), c = cf.value, n = 0;
    rows.forEach(function (r) {
      var show = (!t || (r.getAttribute("data-text") || "").indexOf(t) !== -1) && (!c || r.getAttribute("data-conf") === c);
      r.style.display = show ? "" : "none";
      var nx = r.nextElementSibling;
      if (nx && nx.classList.contains("writerow")) nx.style.display = show ? "" : "none";
      if (show) n++;
    });
    if (count) count.textContent = n + " of " + rows.length + " matches shown";
  }
  q.addEventListener("input", apply); cf.addEventListener("change", apply); apply();
})();
