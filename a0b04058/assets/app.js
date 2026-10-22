
(function () {
  var btn = document.getElementById('menu-btn');
  var sb = document.getElementById('sidebar');
  if (btn && sb) { btn.addEventListener('click', function () { sb.classList.toggle('open'); }); }
  var search = document.getElementById('tbl-search');
  var sportSel = document.getElementById('tbl-sport');
  var confSel = document.getElementById('tbl-conf');
  var countEl = document.getElementById('row-count');
  function applyFilters() {
    var q = search ? search.value.trim().toLowerCase() : '';
    var sp = sportSel ? sportSel.value : '';
    var cf = confSel ? confSel.value : '';
    var rows = document.querySelectorAll('tbody tr[data-filterable="1"]');
    var shown = 0;
    rows.forEach(function (tr) {
      var okQ = !q || tr.textContent.toLowerCase().indexOf(q) !== -1;
      var okS = !sp || tr.getAttribute('data-sport') === sp;
      var okC = !cf || tr.getAttribute('data-conf') === cf;
      var vis = okQ && okS && okC;
      tr.style.display = vis ? '' : 'none';
      if (vis) shown += 1;
    });
    if (countEl && rows.length) { countEl.textContent = 'Showing ' + shown + ' of ' + rows.length + ' rows'; }
  }
  if (search) search.addEventListener('input', applyFilters);
  if (sportSel) sportSel.addEventListener('change', applyFilters);
  if (confSel) confSel.addEventListener('change', applyFilters);
  applyFilters();
})();
