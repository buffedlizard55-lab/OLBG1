(function () {
  function initTableFilter() {
    var table = document.getElementById('master-events-table');
    if (!table) return;
    var search = document.getElementById('filter-search');
    var sportSel = document.getElementById('filter-sport');
    var confSel = document.getElementById('filter-conf');
    var statusSel = document.getElementById('filter-status');
    var readout = document.getElementById('filter-count');
    var rows = Array.prototype.slice.call(table.querySelectorAll('tbody tr'));

    function apply() {
      var q = search ? search.value.trim().toLowerCase() : '';
      var sp = sportSel ? sportSel.value : 'ALL';
      var cf = confSel ? confSel.value : 'ALL';
      var st = statusSel ? statusSel.value : 'ALL';
      var shown = 0;
      rows.forEach(function (tr) {
        var ok = true;
        if (sp !== 'ALL' && tr.getAttribute('data-sport') !== sp) ok = false;
        if (cf !== 'ALL' && tr.getAttribute('data-conf') !== cf) ok = false;
        if (st !== 'ALL' && tr.getAttribute('data-status') !== st) ok = false;
        if (ok && q && tr.textContent.toLowerCase().indexOf(q) === -1) ok = false;
        tr.style.display = ok ? '' : 'none';
        if (ok) shown++;
      });
      if (readout) readout.textContent = 'Showing ' + shown + ' of ' + rows.length + ' reconciled events';
    }

    [search, sportSel, confSel, statusSel].forEach(function (el) {
      if (!el) return;
      el.addEventListener('input', apply);
      el.addEventListener('change', apply);
    });
    apply();
  }

  function initPredFilter() {
    var grid = document.getElementById('pred-cards-grid');
    if (!grid) return;
    var search = document.getElementById('pred-search');
    var sportSel = document.getElementById('pred-sport');
    var readout = document.getElementById('pred-count');
    var cards = Array.prototype.slice.call(grid.querySelectorAll('.pred-card'));

    function apply() {
      var q = search ? search.value.trim().toLowerCase() : '';
      var sp = sportSel ? sportSel.value : 'ALL';
      var shown = 0;
      cards.forEach(function (card) {
        var ok = true;
        if (sp !== 'ALL' && card.getAttribute('data-sport') !== sp) ok = false;
        if (ok && q && card.textContent.toLowerCase().indexOf(q) === -1) ok = false;
        card.style.display = ok ? '' : 'none';
        if (ok) shown++;
      });
      if (readout) readout.textContent = 'Showing ' + shown + ' of ' + cards.length + ' high-confidence predictions';
    }

    [search, sportSel].forEach(function (el) {
      if (!el) return;
      el.addEventListener('input', apply);
      el.addEventListener('change', apply);
    });
    apply();
  }

  document.addEventListener('DOMContentLoaded', function () {
    initTableFilter();
    initPredFilter();
  });
})();
