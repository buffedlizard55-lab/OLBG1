(() => {
  const toggle = document.querySelector('.nav-toggle');
  const nav = document.querySelector('#site-nav');
  if (toggle && nav) {
    toggle.addEventListener('click', () => {
      const open = nav.classList.toggle('open');
      toggle.setAttribute('aria-expanded', String(open));
    });
  }

  const table = document.querySelector('#match-table');
  if (!table) return;
  const sport = document.querySelector('#sport-filter');
  const confidence = document.querySelector('#confidence-filter');
  const search = document.querySelector('#match-search');
  const count = document.querySelector('#filter-count');
  const empty = document.querySelector('#no-filter-results');
  const rows = [...table.tBodies[0].rows];

  function applyFilters() {
    const query = search.value.trim().toLowerCase();
    let visible = 0;
    rows.forEach(row => {
      const sportMatch = sport.value === 'all' || row.dataset.sport === sport.value;
      const tierMatch = confidence.value === 'all' || row.dataset.confidence === confidence.value;
      const searchMatch = !query || row.dataset.search.includes(query);
      const show = sportMatch && tierMatch && searchMatch;
      row.hidden = !show;
      if (show) visible += 1;
    });
    count.textContent = `${visible} row${visible === 1 ? '' : 's'}`;
    empty.hidden = visible !== 0;
  }

  [sport, confidence].forEach(control => control.addEventListener('change', applyFilters));
  search.addEventListener('input', applyFilters);
})();
