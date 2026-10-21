const root = document.body.dataset.root || '.';
const page = document.body.dataset.page || 'home';
const categorySlug = document.body.dataset.category || '';

const escapeHtml = (value = '') => String(value)
  .replaceAll('&', '&amp;')
  .replaceAll('<', '&lt;')
  .replaceAll('>', '&gt;')
  .replaceAll('"', '&quot;')
  .replaceAll("'", '&#039;');

const titleCase = (value = '') => value.replaceAll('-', ' ').replace(/\b\w/g, (letter) => letter.toUpperCase());
const formatDate = (date) => {
  if (!date) return '<span aria-label="Unverified">—</span>';
  return new Intl.DateTimeFormat('en-GB', { day: '2-digit', month: 'short', year: 'numeric', timeZone: 'UTC' })
    .format(new Date(`${date}T00:00:00Z`));
};
const formatCapture = (timestamp) => new Intl.DateTimeFormat('en-GB', {
  day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit', timeZone: 'UTC', timeZoneName: 'short',
}).format(new Date(timestamp));
const badge = (text, kind = '') => `<span class="badge badge-${escapeHtml(kind || text.toLowerCase().replaceAll(' ', '-'))}">${escapeHtml(text)}</span>`;
const sourceLink = (source, label = 'Official source') => `<a class="source-link" href="${escapeHtml(source.url)}" target="_blank" rel="noreferrer">${escapeHtml(label)} ↗</a>`;

let state;

async function loadData() {
  const [matchResponse, categoryResponse] = await Promise.all([
    fetch(`${root}/data/matches.json`),
    fetch(`${root}/data/categories.json`),
  ]);
  if (!matchResponse.ok || !categoryResponse.ok) throw new Error('The frozen data files could not be loaded.');
  const matchData = await matchResponse.json();
  const categoryData = await categoryResponse.json();
  return { matchData, categories: categoryData.categories, matches: matchData.matches };
}

function setText(selector, value) {
  const element = document.querySelector(selector);
  if (element) element.textContent = value;
}

function renderGlobalCounts() {
  const { summary } = state.matchData;
  document.querySelectorAll('[data-count="matches"]').forEach((node) => { node.textContent = summary.matchCount; });
  document.querySelectorAll('[data-count="categories"]').forEach((node) => { node.textContent = state.categories.length; });
  document.querySelectorAll('[data-count="verified"]').forEach((node) => { node.textContent = summary.verifiedCount; });
  document.querySelectorAll('[data-count="flagged"]').forEach((node) => { node.textContent = summary.flaggedMatchCount; });
  document.querySelectorAll('[data-count="high"]').forEach((node) => { node.textContent = summary.highConfidenceCount; });
  document.querySelectorAll('[data-capture]').forEach((node) => { node.textContent = formatCapture(state.matchData.generatedAt); });
}

function renderCategoryGrid(container, limit) {
  if (!container) return;
  const categories = limit ? state.categories.slice(0, limit) : state.categories;
  const html = categories.map((category, index) => {
    const rows = state.matches.filter((match) => match.categorySlug === category.slug);
    const flagged = rows.filter((match) => match.flags.length).length;
    const statusText = category.status === 'verified' ? 'Verified slate' : 'Review notes';
    return `<a class="category-card" data-index="${String(index + 1).padStart(2, '0')}" href="${root}/sports/${escapeHtml(category.slug)}.html">
      <div class="card-top">
        <span class="category-kicker">${escapeHtml(category.kicker)}</span>
        ${badge(statusText, category.status)}
      </div>
      <h3>${escapeHtml(category.name)}</h3>
      <p>${escapeHtml(category.description)}</p>
      <div class="card-meta">
        <span>${rows.length} modeled match${rows.length === 1 ? '' : 'es'}</span>
        <span aria-hidden="true">•</span>
        <span>${flagged} flagged</span>
      </div>
    </a>`;
  }).join('');
  container.innerHTML = html;
}

function matchTableMarkup(matches, options = {}) {
  if (!matches.length) {
    return `<div class="empty-state">
      <div class="empty-state-mark">∅</div>
      <h3>${escapeHtml(options.emptyTitle || 'No match rows')}</h3>
      <p>${escapeHtml(options.emptyText || 'No rows match the current filters. Clear a filter to restore the full frozen capture.')}</p>
      ${options.emptyAction || ''}
    </div>`;
  }
  const rows = matches.map((match) => {
    const date = match.schedule.date ? formatDate(match.schedule.date) : '—';
    const time = match.schedule.time ? `<div class="metric-small">${escapeHtml(match.schedule.time)} ${escapeHtml(match.schedule.timezone)}</div>` : '';
    const origin = match.origin !== 'OLBG visible listing' ? `<span class="metric-small">${badge(match.origin, 'origin')}</span>` : '';
    const flags = match.flags.length ? `<span class="flag-dot" title="Flagged for review" aria-label="Flagged for review"></span>` : '';
    return `<tr>
      <td class="date-cell">${date}${time}</td>
      <td class="match-cell">
        <button class="match-button" type="button" data-open-match="${escapeHtml(match.id)}">${escapeHtml(match.participants.a)} <span aria-hidden="true">v</span> ${escapeHtml(match.participants.b)}${flags}</button>
        <span class="competition">${escapeHtml(match.competition)} · ${escapeHtml(match.sport)}</span>
        ${origin}
      </td>
      <td class="pick-cell"><strong>${escapeHtml(match.model.winner.selection)}</strong><div class="metric-small">${match.model.winner.probabilityPct.toFixed(1)}% · fair ${match.model.winner.fairDecimalOdds.toFixed(2)}</div></td>
      <td class="line-cell">${escapeHtml(match.model.handicap.line)}</td>
      <td class="line-cell">${escapeHtml(match.model.total.line)}<div class="metric-small">midpoint only</div></td>
      <td>${badge(match.model.confidence, match.model.confidence)}</td>
      <td>${badge(match.schedule.verification.replace('-', ' '), match.schedule.verification)}</td>
      <td>${sourceLink(match.sources.official)}</td>
    </tr>`;
  }).join('');
  return `<div class="table-card"><div class="table-scroll">
    <table>
      <thead><tr>
        <th scope="col">Official date</th><th scope="col">Match</th><th scope="col">Winner line</th>
        <th scope="col">Handicap</th><th scope="col">Total</th><th scope="col">Confidence</th>
        <th scope="col">Verification</th><th scope="col">Evidence</th>
      </tr></thead>
      <tbody>${rows}</tbody>
    </table>
  </div></div>`;
}

function attachMatchButtons(scope = document) {
  scope.querySelectorAll('[data-open-match]').forEach((button) => {
    button.addEventListener('click', () => openMatch(button.dataset.openMatch));
  });
}

function renderTable(container, matches, options) {
  container.innerHTML = matchTableMarkup(matches, options);
  attachMatchButtons(container);
}

function openMatch(id) {
  const match = state.matches.find((item) => item.id === id);
  const dialog = document.querySelector('#match-dialog');
  if (!match || !dialog) return;
  const dateLine = match.schedule.date
    ? `${formatDate(match.schedule.date).replace(/<[^>]+>/g, '')}${match.schedule.time ? ` · ${match.schedule.time} ${match.schedule.timezone}` : ''}`
    : 'Date / time unverified';
  const facts = match.sourceFacts.map((fact) => `<li>${escapeHtml(fact)}</li>`).join('');
  const flagBlock = match.flags.length ? `<section class="dialog-section">
      <h3>Flagged for review</h3>
      ${match.flags.map((item) => `<p><strong>${escapeHtml(item.code.replaceAll('_', ' '))}:</strong> ${escapeHtml(item.detail)}</p>`).join('')}
    </section>` : '';
  const analysisBlock = match.model.highConfidenceAnalysis ? `<section class="dialog-section">
      <h3>High-confidence analysis</h3>
      <p class="analysis-quote">${escapeHtml(match.model.highConfidenceAnalysis)}</p>
    </section>` : '';
  dialog.querySelector('[data-dialog-content]').innerHTML = `
    <div class="dialog-head">
      <div><span class="eyebrow">${escapeHtml(match.competition)}</span><h2>${escapeHtml(match.participants.a)} v ${escapeHtml(match.participants.b)}</h2></div>
      <button class="dialog-close" type="button" aria-label="Close details" data-close-dialog>×</button>
    </div>
    <div class="dialog-body">
      <div class="dialog-grid">
        <div class="dialog-stat"><span>Winner</span><strong>${escapeHtml(match.model.winner.selection)} · ${match.model.winner.probabilityPct.toFixed(1)}%</strong></div>
        <div class="dialog-stat"><span>Independent fair odds</span><strong>${match.model.winner.fairDecimalOdds.toFixed(2)}</strong></div>
        <div class="dialog-stat"><span>Confidence</span><strong>${escapeHtml(titleCase(match.model.confidence))}</strong></div>
        <div class="dialog-stat"><span>Handicap midpoint</span><strong>${escapeHtml(match.model.handicap.line)}</strong></div>
        <div class="dialog-stat"><span>Total midpoint</span><strong>${escapeHtml(match.model.total.line)}</strong></div>
        <div class="dialog-stat"><span>Official schedule</span><strong>${escapeHtml(dateLine)}</strong></div>
      </div>
      ${analysisBlock}
      <section class="dialog-section">
        <h3>Official evidence recorded</h3>
        <ul>${facts}</ul>
        <p>${sourceLink(match.sources.official, match.sources.official.label)}</p>
        <p><a class="source-link" href="${escapeHtml(match.sources.discovery.url)}" target="_blank" rel="noreferrer">OLBG discovery row (not verification) ↗</a></p>
      </section>
      <section class="dialog-section">
        <h3>Reproducible model inputs</h3>
        <p>${escapeHtml(match.model.rationale)}</p>
        <p><strong>Formula:</strong> ${escapeHtml(match.model.formula)}</p>
        <p><strong>Inputs relative to ${escapeHtml(match.participants.a)}:</strong> strength ${match.model.inputs.strengthEdgeA}; form ${match.model.inputs.formEdgeA}; venue ${match.model.inputs.venueEdgeA}; reliability ${match.model.inputs.appliedReliability}.</p>
        <p><strong>Independence:</strong> ${escapeHtml(match.model.independenceStatement)}</p>
      </section>
      ${flagBlock}
      <section class="dialog-section">
        <h3>Audit note</h3>
        <p>${escapeHtml(match.audit.valuesRule)}</p>
      </section>
    </div>`;
  dialog.querySelector('[data-close-dialog]').addEventListener('click', () => dialog.close());
  dialog.showModal();
}

function renderHome() {
  renderCategoryGrid(document.querySelector('[data-category-grid]'));
  const high = state.matches
    .filter((match) => match.model.confidence === 'high')
    .sort((a, b) => b.model.winner.probabilityPct - a.model.winner.probabilityPct)
    .slice(0, 6);
  const pickList = document.querySelector('[data-high-picks]');
  if (pickList) {
    pickList.innerHTML = high.map((match, index) => `<button class="pick-list-item match-button" data-open-match="${escapeHtml(match.id)}" type="button">
      <span class="rank">${index + 1}</span>
      <span><strong>${escapeHtml(match.model.winner.selection)}</strong><small>${escapeHtml(match.participants.a)} v ${escapeHtml(match.participants.b)}</small></span>
      <span class="probability">${match.model.winner.probabilityPct.toFixed(1)}%</span>
    </button>`).join('');
    attachMatchButtons(pickList);
  }
  const flagged = state.matches.filter((match) => match.flags.length).slice(0, 5);
  const auditList = document.querySelector('[data-audit-preview]');
  if (auditList) {
    auditList.innerHTML = flagged.map((match) => `<div class="audit-item">
      <span class="audit-icon">!</span>
      <div><strong>${escapeHtml(match.participants.a)} v ${escapeHtml(match.participants.b)}</strong><p>${escapeHtml(match.flags[0].detail)}</p></div>
    </div>`).join('');
  }
}

function renderMatches() {
  const container = document.querySelector('[data-match-table]');
  const search = document.querySelector('#search');
  const sport = document.querySelector('#sport');
  const confidence = document.querySelector('#confidence');
  const verification = document.querySelector('#verification');
  const flagsOnly = document.querySelector('#flags-only');
  if (!container) return;

  sport.innerHTML = `<option value="">All included sports</option>${state.categories
    .filter((category) => state.matches.some((match) => match.categorySlug === category.slug))
    .map((category) => `<option value="${escapeHtml(category.slug)}">${escapeHtml(category.name)}</option>`).join('')}`;

  const apply = () => {
    const query = search.value.trim().toLowerCase();
    const filtered = state.matches.filter((match) => {
      const haystack = `${match.participants.a} ${match.participants.b} ${match.competition} ${match.sport}`.toLowerCase();
      return (!query || haystack.includes(query))
        && (!sport.value || match.categorySlug === sport.value)
        && (!confidence.value || match.model.confidence === confidence.value)
        && (!verification.value || match.schedule.verification === verification.value)
        && (flagsOnly.getAttribute('aria-pressed') !== 'true' || match.flags.length > 0);
    }).sort(sortMatches);
    setText('[data-results-count]', `${filtered.length} of ${state.matches.length} rows`);
    renderTable(container, filtered);
  };
  [search, sport, confidence, verification].forEach((control) => control.addEventListener(control === search ? 'input' : 'change', apply));
  flagsOnly.addEventListener('click', () => {
    flagsOnly.setAttribute('aria-pressed', String(flagsOnly.getAttribute('aria-pressed') !== 'true'));
    apply();
  });
  apply();
}

function sortMatches(a, b) {
  const dateA = a.schedule.date || '9999-99-99';
  const dateB = b.schedule.date || '9999-99-99';
  return dateA.localeCompare(dateB) || a.categorySlug.localeCompare(b.categorySlug) || a.id.localeCompare(b.id);
}

function renderCategory() {
  const category = state.categories.find((item) => item.slug === categorySlug);
  if (!category) return;
  const rows = state.matches.filter((match) => match.categorySlug === categorySlug).sort(sortMatches);
  const flagged = rows.filter((match) => match.flags.length).length;
  const verified = rows.filter((match) => match.schedule.verification === 'verified').length;
  setText('[data-category-name]', category.name);
  setText('[data-category-kicker]', category.kicker);
  setText('[data-category-description]', category.description);
  setText('[data-category-count]', rows.length);
  setText('[data-category-verified]', verified);
  setText('[data-category-flagged]', flagged);
  const status = document.querySelector('[data-category-status]');
  if (status) status.innerHTML = badge(category.status === 'verified' ? 'Verified slate' : 'Review notes', category.status);
  const notice = document.querySelector('[data-category-notice]');
  if (notice && category.emptyReason) {
    notice.hidden = false;
    notice.querySelector('strong').textContent = category.emptyReason === 'OUTRIGHTS_ONLY' ? 'No match-level rows in this capture' : 'Official race-card inputs unavailable';
    notice.querySelector('span:last-child').textContent = category.description;
  }
  const container = document.querySelector('[data-category-table]');
  renderTable(container, rows, {
    emptyTitle: 'No match-level rows to model',
    emptyText: category.description,
    emptyAction: `<div class="actions" style="justify-content:center">${category.officialSource ? sourceLink(category.officialSource, category.officialSource.label) : ''}<a class="button button-paper" href="${root}/flagged.html">Open review log</a></div>`,
  });
}

function renderFlagged() {
  const flagged = state.matches.flatMap((match) => match.flags.map((item) => ({ match, ...item })));
  const counts = {
    critical: flagged.filter((item) => item.severity === 'critical').length,
    review: flagged.filter((item) => item.severity === 'review').length,
    info: flagged.filter((item) => item.severity === 'info').length,
    unverified: state.matches.filter((match) => match.schedule.verification !== 'verified').length,
  };
  Object.entries(counts).forEach(([key, value]) => setText(`[data-flag-count="${key}"]`, value));
  setText('[data-flag-total]', flagged.length);
  const tbody = document.querySelector('[data-flag-rows]');
  if (!tbody) return;
  tbody.innerHTML = flagged.map((item) => `<tr class="severity-${escapeHtml(item.severity)}">
    <td>${badge(item.severity, item.severity)}</td>
    <td class="match-cell"><button class="match-button" type="button" data-open-match="${escapeHtml(item.match.id)}">${escapeHtml(item.match.participants.a)} v ${escapeHtml(item.match.participants.b)}</button><span class="competition">${escapeHtml(item.match.competition)}</span></td>
    <td><strong>${escapeHtml(item.code.replaceAll('_', ' '))}</strong></td>
    <td class="flag-detail">${escapeHtml(item.detail)}</td>
    <td>${sourceLink(item.match.sources.official)}</td>
  </tr>`).join('');
  attachMatchButtons(tbody);

  const categoryIssues = state.categories.filter((category) => category.emptyReason || category.status === 'review');
  const issueList = document.querySelector('[data-category-issues]');
  if (issueList) {
    issueList.innerHTML = categoryIssues.map((category) => `<a class="category-card" data-index="↗" href="${root}/sports/${escapeHtml(category.slug)}.html">
      <div class="card-top"><span class="category-kicker">Coverage note</span>${badge('review', 'review')}</div>
      <h3>${escapeHtml(category.name)}</h3><p>${escapeHtml(category.description)}</p>
      <div class="card-meta"><span>${escapeHtml(category.emptyReason || 'ROW_LEVEL_FLAGS')}</span></div>
    </a>`).join('');
  }
}

function renderMethodology() {
  const { methodology, summary } = state.matchData;
  setText('[data-model-version]', methodology.modelVersion);
  setText('[data-method-count]', summary.matchCount);
  setText('[data-method-high]', summary.highConfidenceCount);
  const formula = document.querySelector('[data-formula]');
  if (formula) formula.textContent = state.matches[0].model.formula;
}

function setupDialog() {
  const dialog = document.querySelector('#match-dialog');
  if (!dialog) return;
  dialog.addEventListener('click', (event) => {
    if (event.target === dialog) dialog.close();
  });
  dialog.addEventListener('cancel', () => dialog.close());
}

async function init() {
  try {
    state = await loadData();
    renderGlobalCounts();
    setupDialog();
    if (page === 'home') renderHome();
    if (page === 'matches') renderMatches();
    if (page === 'category') renderCategory();
    if (page === 'flagged') renderFlagged();
    if (page === 'methodology') renderMethodology();
    document.querySelectorAll('.loading').forEach((node) => node.classList.remove('loading'));
  } catch (error) {
    console.error(error);
    document.querySelectorAll('.loading').forEach((node) => {
      node.classList.remove('loading');
      node.innerHTML = `<strong>Data unavailable.</strong><br>${escapeHtml(error.message)}`;
    });
  }
}

init();
