import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { execFileSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const readJson = (file) => JSON.parse(fs.readFileSync(path.join(root, file), 'utf8'));
const words = (value = '') => (value.match(/[\p{L}\p{N}’'-]+/gu) || []).length;

const data = readJson('data/matches.json');
const categoryData = readJson('data/categories.json');

test('frozen capture has the expected included scope', () => {
  assert.equal(data.matches.length, 135);
  assert.equal(categoryData.categories.length, 15);
  assert.equal(new Set(data.matches.map((row) => row.id)).size, 135);
  assert.deepEqual(
    [...new Set(data.matches.map((row) => row.categorySlug))].sort(),
    ['baseball','basketball','cricket','darts','gaelic-football','handball','ice-hockey','rugby-union','snooker','tennis','volleyball'],
  );
});

test('volatile Rugby Union capture matches the latest line-by-line recapture', () => {
  const rugby = data.matches
    .filter((row) => row.categorySlug === 'rugby-union')
    .map((row) => `${row.participants.a}—${row.participants.b}`);
  assert.deepEqual(rugby, [
    'Montauban—Oyonnax', 'Agen—Nissa', 'Soyaux-Angoulême—Dax', 'Connacht—Zebre Parma',
    'Narbonne—Brive', 'Aurillac—Nevers', 'Bulls—Ulster', 'Valence Romans—Colomiers',
    'Grenoble—Biarritz', 'Provence Rugby—Béziers', 'Stormers—Scarlets', 'Bayonne—Lyon',
    'Stade Toulousain—Perpignan', 'Leinster—Munster', 'La Rochelle—Bordeaux-Bègles',
  ]);
  assert.ok(data.matches.filter((row) => row.categorySlug === 'rugby-union').every((row) => row.schedule.time && row.schedule.timezone));
});

test('known Gaelic Football start times use official county-board values', () => {
  const times = Object.fromEntries(data.matches
    .filter((row) => row.categorySlug === 'gaelic-football')
    .map((row) => [row.id, row.schedule.time]));
  assert.deepEqual(times, {
    '2026-10-25-nemo-rangers-st-finbarrs': '16:00',
    '2026-10-24-salthill-knocknacarra-maigh-cuilinn': '19:00',
    '2026-11-01-ire-g-kanturk': '14:00',
    '2026-10-25-rathgormack-the-nire': '14:30',
  });
});

test('every non-match category has an official manual-review source', () => {
  const empty = categoryData.categories.filter((category) => category.emptyReason);
  assert.equal(empty.length, 4);
  for (const category of empty) {
    assert.match(category.officialSource.url, /^https:\/\//, category.slug);
    assert.ok(category.officialSource.label, category.slug);
  }
});

test('all table rows expose official evidence and three modeled markets', () => {
  for (const row of data.matches) {
    assert.match(row.sources.official.url, /^https:\/\//, row.id);
    assert.doesNotMatch(row.sources.official.url, /olbg\.com/, row.id);
    assert.ok(row.sources.official.label, row.id);
    assert.ok(row.model.winner.selection, row.id);
    assert.ok(row.model.handicap.line, row.id);
    assert.ok(row.model.total.line, row.id);
    assert.match(row.model.independenceStatement, /excluded/i, row.id);
  }
});

test('unverified source values remain blank and confidence remains low', () => {
  const unverified = data.matches.filter((row) => row.schedule.verification === 'unverified');
  assert.equal(unverified.length, 3);
  for (const row of unverified) {
    assert.equal(row.schedule.date, '', row.id);
    assert.equal(row.schedule.time, '', row.id);
    assert.equal(row.schedule.venue, '', row.id);
    assert.equal(row.model.confidence, 'low', row.id);
    assert.ok(row.flags.length > 0, row.id);
  }
});

test('high-confidence copy is unique, source-grounded and at least 30 words', () => {
  const high = data.matches.filter((row) => row.model.confidence === 'high');
  assert.equal(high.length, 10);
  const copy = new Set();
  for (const row of high) {
    assert.ok(words(row.model.highConfidenceAnalysis) >= 30, row.id);
    assert.match(row.model.highConfidenceAnalysis.toLocaleLowerCase(), new RegExp(row.model.winner.selection.split(' ')[0].toLocaleLowerCase()), row.id);
    assert.equal(row.schedule.verification, 'verified', row.id);
    assert.ok(row.sourceFacts.length >= 2, row.id);
    copy.add(row.model.highConfidenceAnalysis);
  }
  assert.equal(copy.size, high.length);
});

test('probabilities and no-vig prices are internally coherent', () => {
  for (const row of data.matches) {
    const winner = row.model.winner;
    assert.ok(Math.abs(winner.participantAProbabilityPct + winner.participantBProbabilityPct - 100) <= 0.11, row.id);
    assert.ok(Math.abs((100 / winner.probabilityPct) - winner.fairDecimalOdds) < 0.02, row.id);
    assert.ok(winner.probabilityPct >= 50 && winner.probabilityPct < 100, row.id);
  }
});

test('model build is deterministic', () => {
  const file = path.join(root, 'data/matches.json');
  const before = crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');
  execFileSync(process.execPath, ['scripts/build-model.mjs'], { cwd: root, stdio: 'pipe' });
  const after = crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');
  assert.equal(after, before);
});

test('every category has a generated subpage and all core pages load the app', () => {
  for (const category of categoryData.categories) {
    const page = path.join(root, 'sports', `${category.slug}.html`);
    assert.ok(fs.existsSync(page), category.slug);
    const html = fs.readFileSync(page, 'utf8');
    assert.match(html, /data-page="category"/);
    assert.match(html, /assets\/app\.js/);
  }
  for (const name of ['index.html', 'matches.html', 'flagged.html', 'methodology.html']) {
    const html = fs.readFileSync(path.join(root, name), 'utf8');
    assert.match(html, /assets\/styles\.css/);
    assert.match(html, /assets\/app\.js/);
    assert.doesNotMatch(html, /localhost|127\.0\.0\.1/);
  }
});
