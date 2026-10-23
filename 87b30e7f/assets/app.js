(function () {
  var searchEl = document.getElementById('desk-search');
  var sportEl = document.getElementById('desk-sport');
  var confEl = document.getElementById('desk-conf');
  var fmtEl = document.getElementById('desk-odds-fmt');
  var countEl = document.getElementById('desk-count');
  var clearBtn = document.getElementById('desk-clear');

  function applyFilters() {
    var q = searchEl ? searchEl.value.trim().toLowerCase() : '';
    var sp = sportEl ? sportEl.value : '';
    var cf = confEl ? confEl.value : '';
    var items = document.querySelectorAll('[data-filter-item]');
    var shown = 0;
    items.forEach(function (el) {
      var hay = (el.getAttribute('data-haystack') || '').toLowerCase();
      var itemSp = el.getAttribute('data-sport') || '';
      var itemCf = el.getAttribute('data-conf') || '';
      var ok = (!q || hay.indexOf(q) !== -1) && (!sp || itemSp === sp) && (!cf || itemCf === cf);
      el.style.display = ok ? '' : 'none';
      if (ok) shown += 1;
    });
    if (countEl) countEl.textContent = shown + ' of ' + items.length + ' shown';
  }

  function applyOddsFormat() {
    if (!fmtEl) return;
    var mode = fmtEl.value;
    document.querySelectorAll('[data-am][data-dec]').forEach(function (el) {
      el.textContent = mode === 'decimal' ? el.getAttribute('data-dec') : el.getAttribute('data-am');
    });
  }

  if (searchEl) searchEl.addEventListener('input', applyFilters);
  if (sportEl) sportEl.addEventListener('change', applyFilters);
  if (confEl) confEl.addEventListener('change', applyFilters);
  if (fmtEl) fmtEl.addEventListener('change', applyOddsFormat);
  if (clearBtn) {
    clearBtn.addEventListener('click', function () {
      if (searchEl) searchEl.value = '';
      if (sportEl) sportEl.value = '';
      if (confEl) confEl.value = '';
      applyFilters();
    });
  }
  if (countEl) applyFilters();
})();
