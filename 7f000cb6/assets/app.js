(function () {
  var btn = document.getElementById('menu-btn');
  var sb = document.getElementById('sidebar');
  if (btn && sb) {
    btn.addEventListener('click', function () {
      sb.classList.toggle('open');
    });
  }

  var search = document.getElementById('tbl-search');
  var sportSel = document.getElementById('tbl-sport');
  var confSel = document.getElementById('tbl-conf');
  var oddsSel = document.getElementById('odds-fmt');
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
    if (countEl && rows.length) {
      countEl.textContent = 'Showing ' + shown + ' of ' + rows.length + ' rows';
    }
  }

  if (search) search.addEventListener('input', applyFilters);
  if (sportSel) sportSel.addEventListener('change', applyFilters);
  if (confSel) confSel.addEventListener('change', applyFilters);

  if (oddsSel) {
    oddsSel.addEventListener('change', function () {
      var mode = oddsSel.value;
      document.querySelectorAll('.odds-val').forEach(function (el) {
        var us = el.getAttribute('data-us');
        var dec = el.getAttribute('data-dec');
        if (mode === 'decimal') {
          el.innerHTML = dec + ' <small>(' + us + ')</small>';
        } else {
          el.innerHTML = us + ' <small>(' + dec + ')</small>';
        }
      });
    });
  }

  var nowMs = Date.now();
  var elapsed = 0;
  document.querySelectorAll('tr[data-start-utc]').forEach(function (tr) {
    var iso = tr.getAttribute('data-start-utc');
    if (iso) {
      var t = Date.parse(iso);
      if (!isNaN(t) && t <= nowMs) {
        tr.classList.add('is-elapsed');
        elapsed += 1;
      }
    }
  });
  var expNote = document.getElementById('live-expiry-note');
  if (expNote && elapsed > 0) {
    expNote.hidden = false;
    expNote.textContent = elapsed + ' scheduled kickoff(s) on this page have now elapsed in real time and are marked historical.';
  }
  applyFilters();
})();
