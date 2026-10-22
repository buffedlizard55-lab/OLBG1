/* Browser contract tests. Dependencies are pinned in the workflow; no production JS dependencies. */
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),http=require('node:http'),os=require('node:os'),zlib=require('node:zlib'),cp=require('node:child_process');
const {chromium}=require('playwright-core'),bundle=require('@sparticuz/chromium');
const site=path.resolve(process.env.SITE_DIR||'_site');
const shots=path.resolve('.test-results');fs.mkdirSync(shots,{recursive:true});
const snapshot=JSON.parse(fs.readFileSync(path.join(site,'data/current/snapshot.json'),'utf8'));
const server=http.createServer((req,res)=>{
  let pathname;try{pathname=decodeURIComponent(new URL(req.url,'http://test.invalid').pathname);}catch{res.writeHead(400).end();return;}
  if(pathname.startsWith('/OLBG1/'))pathname=pathname.slice(6);
  let file=path.resolve(site,'.'+pathname);if(!file.startsWith(site+path.sep)&&file!==site){res.writeHead(403).end();return;}
  if(fs.existsSync(file)&&fs.statSync(file).isDirectory())file=path.join(file,'index.html');
  if(!fs.existsSync(file)){res.writeHead(404,{'Content-Type':'text/html'}).end(fs.readFileSync(path.join(site,'404.html')));return;}
  const types={'.html':'text/html; charset=utf-8','.css':'text/css','.js':'text/javascript','.json':'application/json','.svg':'image/svg+xml','.csv':'text/csv'};
  res.writeHead(200,{'Content-Type':types[path.extname(file)]||'application/octet-stream'});fs.createReadStream(file).pipe(res);
});
(async()=>{
  // The npm bundle supplies Chromium and its portable NSS libraries. No apt/CDN dependency.
  const pkgDir=path.dirname(require.resolve('@sparticuz/chromium'));
  const libPack=path.resolve(pkgDir,'../../bin/al2023.tar.br');
  const libDir=path.join(os.tmpdir(),'olbg-browser-libs');fs.mkdirSync(libDir,{recursive:true});
  if(fs.existsSync(libPack)&&!fs.existsSync(path.join(libDir,'lib/libnspr4.so'))){
    const result=cp.spawnSync('tar',['-xf','-','-C',libDir],{input:zlib.brotliDecompressSync(fs.readFileSync(libPack))});assert.equal(result.status,0);
  }
  process.env.LD_LIBRARY_PATH=path.join(libDir,'lib')+(process.env.LD_LIBRARY_PATH?':'+process.env.LD_LIBRARY_PATH:'');
  await new Promise(r=>server.listen(0,'0.0.0.0',r));const base=`http://127.0.0.1:${server.address().port}/OLBG1/`;
  let browser;
  try{
    browser=await chromium.launch({executablePath:await bundle.executablePath(),args:bundle.args.filter(x=>!["--single-process","--disable-web-security","--disable-site-isolation-trials"].includes(x)),headless:true});
    const context=await browser.newContext({viewport:{width:1500,height:1050},deviceScaleFactor:1,acceptDownloads:true});
    const page=await context.newPage();const errors=[],badResponses=[];
    page.on('pageerror',x=>errors.push(x.message));page.on('response',r=>{if(r.url().startsWith(base)&&r.status()>=400)badResponses.push(r.url());});
    // Exercise a snapshot as of its build, regardless of when CI tests an archived import.
    await page.clock.install({time:new Date(snapshot.generated_at)});
    await page.goto(base,{waitUntil:'networkidle'});assert.match(await page.title(),/OLBG Research/);
    assert.equal(await page.locator('h1').textContent(),'The match research desk.');
    assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),'Desktop has page-level overflow');
    assert.ok(await page.locator('.compact-table').evaluate(el=>el.scrollWidth<=el.parentElement.clientWidth+1),'Dashboard source table should fit desktop');
    await page.screenshot({path:path.join(shots,'dashboard-desktop.png'),fullPage:true});
    await page.goto(base+'picks.html');assert.equal(await page.locator('#match-table tbody tr').count(),snapshot.fixtures.filter(r=>r.in_window).length);
    await page.locator('#sport-filter').selectOption('ice-hockey');
    assert.equal(await page.locator('#match-table tbody tr:visible').count(),snapshot.fixtures.filter(r=>r.in_window&&r.sport==='ice-hockey').length);
    await page.locator('#search').fill('definitely-not-a-real-match-257e');assert.equal(await page.locator('#match-table tbody tr:visible').count(),0);assert.ok(await page.locator('#no-results').isVisible());
    await page.locator('#clear-filters').click();assert.equal(await page.locator('#search').inputValue(),'');
    await page.locator('#priced-only').check();const priced=snapshot.prices.filter(p=>p.markets.length).length;
    assert.equal(await page.locator('#match-table tbody tr:visible').count(),priced);
    if(priced){
      await page.locator('#odds-format').selectOption('decimal');const p=page.locator('[data-american]:visible').first();assert.equal(await p.textContent(),await p.getAttribute('data-decimal'));
      await page.locator('#odds-format').selectOption('american');assert.equal(await p.textContent(),await p.getAttribute('data-american'));
    }
    await page.locator('#clear-filters').click();
    const download=page.waitForEvent('download');await page.locator('#export-visible').click();const file=await download;assert.match(file.suggestedFilename(),/\.csv$/);
    await page.locator('[data-sort]').click();assert.equal(await page.locator('th[aria-sort]').first().getAttribute('aria-sort'),'descending');
    const first=snapshot.fixtures.find(r=>r.in_window);await page.goto(base+'verification.html#'+first.id);assert.ok(await page.locator('[id="'+first.id+'"]').evaluate(e=>e.open));
    await page.goto(base+'markets.html');assert.equal(await page.locator('.market-book').count(),priced);
    await page.locator('#search').fill('does-not-exist');assert.equal(await page.locator('.market-book:visible').count(),0);await page.locator('#clear-filters').click();
    await page.goto(base+'sports/darts.html');assert.match(await page.locator('main').textContent(),/No verified match rows/);assert.ok(await page.locator('#export-visible').isDisabled());
    await page.goto(base+'predictions.html');assert.match(await page.locator('main').textContent(),/No selection passes/);
    // Expiry must remove displayed selections, probabilities and prices—not only change a badge.
    await page.goto(base+'picks.html');await page.clock.setFixedTime(new Date(Date.parse(snapshot.generated_at)+48*3600*1000));await page.reload();
    assert.ok(await page.locator('#expiry-alert').isVisible());assert.ok((await page.locator('[data-price-value]').allTextContents()).every(x=>x.trim()===''),'Expired price content remained visible');
    assert.equal(await page.locator('[data-record][data-priced="true"]').count(),0);
    await context.close();
    const mobile=await browser.newContext({viewport:{width:390,height:844},isMobile:true,deviceScaleFactor:1});const mp=await mobile.newPage();await mp.clock.install({time:new Date(snapshot.generated_at)});
    await mp.goto(base);assert.ok(await mp.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),'Mobile page overflows');
    await mp.locator('#menu-button').click();assert.equal(await mp.locator('#menu-button').getAttribute('aria-expanded'),'true');assert.ok(await mp.locator('#sidebar').evaluate(e=>e.classList.contains('open')));
    await mp.locator('#sidebar-shade').click({position:{x:350,y:500}});assert.equal(await mp.locator('#menu-button').getAttribute('aria-expanded'),'false');
    await mp.screenshot({path:path.join(shots,'dashboard-mobile.png'),fullPage:true});
    await mp.goto(base+'picks.html');await mp.locator('#search').fill('Boston');assert.ok(await mp.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),'Mobile table escaped scrolling wrapper');
    await mobile.close();
    const plain=await browser.newContext({javaScriptEnabled:false});const pp=await plain.newPage();await pp.goto(base+'picks.html');assert.equal(await pp.locator('#match-table tbody tr').count(),snapshot.fixtures.filter(r=>r.in_window).length);await plain.close();
    assert.deepEqual(errors,[],'Client JavaScript errors');assert.deepEqual(badResponses,[],'Broken browser resource/link responses');
    console.log('Browser PASS: desktop/mobile, project subpath, table filters, empty state, reset, sort, odds toggle, CSV download, evidence deep-link, market search, expiry, no-JS rows.');
  }finally{if(browser)await browser.close();await new Promise(r=>server.close(r));}
})().catch(e=>{console.error(e);process.exitCode=1;server.close();});
