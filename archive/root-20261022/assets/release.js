/* Progressive enhancement only: every fact, row and source is present without JavaScript. */
(() => {
  'use strict';
  const toolbar = document.querySelector('[data-toolbar]');
  function filter() {
    if (!toolbar) return;
    const query = (toolbar.querySelector('input[type="search"]')?.value || '').toLowerCase().trim();
    const sport = toolbar.querySelector('select')?.value || '';
    let count = 0;
    document.querySelectorAll('tr[data-search]').forEach(row => {
      const matched = (!query || row.dataset.search.toLowerCase().includes(query)) && (!sport || row.dataset.sport === sport);
      row.hidden = !matched;
      if (matched) count++;
    });
    const output = toolbar.querySelector('[data-result-count]');
    if (output) output.textContent = `${count} matching rows`;
  }
  toolbar?.addEventListener('input', filter);
  toolbar?.addEventListener('change', filter);
  filter();
  function expire() {
    const now = Date.now();
    document.querySelectorAll('tr[data-start],article[data-start]').forEach(row => {
      const start = Date.parse(row.dataset.start || '');
      const expiry = Date.parse(row.dataset.expires || '');
      let state = '';
      if (Number.isFinite(start) && start <= now) state = 'Start passed since build';
      else if (Number.isFinite(expiry) && expiry <= now) state = 'Evidence expired since build';
      if (!state) return;
      row.classList.add('expired');
      const status = row.querySelector('[data-live-status]');
      if (status) status.textContent = state;
      row.querySelectorAll('[data-live-projection]').forEach(cell => {
        cell.textContent = '';
        cell.setAttribute('aria-label', 'Withdrawn: ' + state);
      });
    });
  }
  expire();
  window.setInterval(expire, 60000);
})();
