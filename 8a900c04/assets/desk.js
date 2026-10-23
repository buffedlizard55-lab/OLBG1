/* Client-side instant search, sport/tier filtering & live count for 8a900c04 */
(function () {
  function initFilters() {
    var search = document.getElementById('desk-search');
    var sportSel = document.getElementById('desk-sport');
    var confSel = document.getElementById('desk-conf');
    var countEl = document.getElementById('desk-visible-count');
    var rows = Array.prototype.slice.call(document.querySelectorAll('tr.pick-row'));
    if (!rows.length) return;

    function apply() {
      var q = search ? search.value.trim().toLowerCase() : '';
      var sp = sportSel ? sportSel.value : 'ALL';
      var cf = confSel ? confSel.value : 'ALL';
      var shown = 0;
      rows.forEach(function (r) {
        var rSport = r.getAttribute('data-sport') || '';
        var rConf = r.getAttribute('data-conf') || '';
        var rChalk = r.getAttribute('data-chalk') || '0';
        var txt = r.textContent.toLowerCase();
        var okSport = (sp === 'ALL') || (rSport === sp);
        var okConf = (cf === 'ALL') ||
          (cf === 'chalk' ? rChalk === '1' : rConf === cf);
        var okQ = (!q) || txt.indexOf(q) !== -1;
        if (okSport && okConf && okQ) {
          r.style.display = '';
          shown += 1;
        } else {
          r.style.display = 'none';
        }
      });
      if (countEl) countEl.textContent = shown + ' of ' + rows.length + ' verified events shown';
    }

    if (search) search.addEventListener('input', apply);
    if (sportSel) sportSel.addEventListener('change', apply);
    if (confSel) confSel.addEventListener('change', apply);
    apply();
  }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initFilters);
  } else {
    initFilters();
  }
})();
