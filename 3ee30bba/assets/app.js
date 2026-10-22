(() => {
  const search = document.getElementById('table-search');
  const sport = document.getElementById('sport-filter');
  const tier = document.getElementById('tier-filter');
  const fmt = document.getElementById('odds-format');
  const clearBtn = document.getElementById('clear-filters');
  const countEl = document.getElementById('filter-count');

  function applyFilters() {
    const q = (search ? search.value : '').trim().toLowerCase();
    const sp = sport ? sport.value : '';
    const tr = tier ? tier.value : '';
    const rows = document.querySelectorAll('tbody tr[data-filterable="1"]');
    if (!rows.length) return;
    let shown = 0;
    rows.forEach((row) => {
      const hay = (row.getAttribute('data-search') || '').toLowerCase();
      const rSp = row.getAttribute('data-sport') || '';
      const rTr = row.getAttribute('data-tier') || '';
      const ok = (!q || hay.includes(q)) && (!sp || rSp === sp) && (!tr || rTr === tr);
      row.hidden = !ok;
      if (ok) shown += 1;
    });
    if (countEl) countEl.textContent = `Showing ${shown} of ${rows.length} rows`;
  }

  function applyOddsFormat() {
    if (!fmt) return;
    const mode = fmt.value;
    document.querySelectorAll('[data-us][data-dec]').forEach((el) => {
      el.textContent = mode === 'decimal' ? el.getAttribute('data-dec') : el.getAttribute('data-us');
    });
  }

  [search, sport, tier].forEach((el) => { if (el) el.addEventListener('input', applyFilters); if (el) el.addEventListener('change', applyFilters); });
  if (fmt) fmt.addEventListener('change', applyOddsFormat);
  if (clearBtn) clearBtn.addEventListener('click', () => {
    if (search) search.value = '';
    if (sport) sport.value = '';
    if (tier) tier.value = '';
    applyFilters();
  });
  applyFilters();
})();
