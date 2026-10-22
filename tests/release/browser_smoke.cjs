/* Optional offline-browser smoke test. Install playwright-core and @sparticuz/chromium
 * into .cache/browser (ignored), then run against the internal local preview server.
 * This testing URL is never shipped as an application API/base URL.
 */
const path = require('node:path');
const fs = require('node:fs');
const assert = require('node:assert/strict');
const modules = path.resolve(__dirname, '../../.cache/browser/node_modules');
const { chromium: playwright } = require(path.join(modules, 'playwright-core'));
const { pathToFileURL } = require('node:url');
const root = path.resolve(__dirname, '../..');
const base = process.env.PREVIEW_URL || 'http://127.0.0.1:8000/';
(async () => {
  const { default: chromium, inflate, setupLambdaEnvironment } = await import(pathToFileURL(path.join(modules, '@sparticuz/chromium/build/index.js')).href);
  await inflate(path.join(modules, '@sparticuz/chromium/bin/al2023.tar.br'));
  setupLambdaEnvironment('/tmp/al2023/lib');
  const browser = await playwright.launch({ executablePath: await chromium.executablePath(), args: chromium.args, headless: true });
  const page = await browser.newPage({ viewport: { width: 1440, height: 1080 } });
  const errors = [];
  page.on('pageerror', error => errors.push(error.message));
  page.on('console', message => { if (message.type() === 'error') errors.push(message.text()); });
  const manifest = JSON.parse(fs.readFileSync(path.join(root, 'data/release/build.json')));
  for (const route of manifest.pages) {
    const response = await page.request.get(new URL(route, base).href);
    assert.equal(response.status(), 200, route + ' should load');
  }
  await page.goto(base);
  await page.getByRole('heading', { name: 'A clearer view of the slate.' }).waitFor();
  const expected = JSON.parse(fs.readFileSync(path.join(root, 'data/release/bundle.json'))).fixtures.filter(f => f.status === 'scheduled' && f.markets.length).length;
  assert.equal(await page.locator('tr[data-search]').count(), expected);
  const search = page.getByRole('searchbox');
  await search.fill('Boston');
  assert.equal(await page.locator('tr[data-search]:visible').count(), 1);
  await search.fill('');
  await page.getByRole('combobox').selectOption('basketball');
  assert.equal(await page.locator('tr[data-search]:visible').count(), 9);
  await page.getByRole('combobox').selectOption('');
  await page.screenshot({ path: path.join(root, '.cache/release-desktop.png'), fullPage: true });
  await page.goto(new URL('sports/handball.html', base).href);
  await page.locator('#model-ehf-oct22-4 > summary').click();
  assert.equal(await page.locator('#model-ehf-oct22-4').getByRole('cell', { name: 'Draw', exact: true }).isVisible(), true);
  await page.goto(new URL('sports/tennis.html', base).href);
  const when = await page.locator('tr[data-search]').first().locator('td').nth(1).innerText();
  assert.match(when, /timezone not confirmed/);
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto(base);
  const dimensions = await page.evaluate(() => ({ viewport: innerWidth, width: document.documentElement.scrollWidth }));
  assert.ok(dimensions.width <= dimensions.viewport + 1, 'No page-level mobile horizontal overflow');
  await page.screenshot({ path: path.join(root, '.cache/release-mobile.png'), fullPage: true });
  await page.clock.install({ time: new Date('2026-10-23T12:00:00Z') });
  await page.reload();
  const surviving = await page.locator('[data-live-projection]').evaluateAll(cells => cells.filter(c => c.textContent.trim()).length);
  assert.equal(surviving, 0, 'Browser expiry withdraws all expired current projections');
  assert.deepEqual(errors, [], 'No browser script / resource errors');
  console.log(JSON.stringify({ result: 'PASS', routes: manifest.pages.length, desktop: '1440x1080', mobile: '390x844', checks: ['route HTTP status', 'search', 'sport filter', 'draw preserved', 'unknown timezone blank UTC', 'no mobile body overflow', 'client expiry', 'no console errors'] }, null, 2));
  await browser.close();
})().catch(error => { console.error(error); process.exit(1); });
