/* Read-only UI gates for this independent desk; tooling stays outside the repo. */
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),http=require('node:http'),os=require('node:os'),zlib=require('node:zlib'),cp=require('node:child_process');
const {chromium}=require('playwright-core'),bundle=require('@sparticuz/chromium');
const root=path.resolve(process.env.SITE_DIR||'.');
const desk=JSON.parse(fs.readFileSync(path.join(root,'data/455acb16/desk.json'),'utf8'));
const shots=path.resolve('.test-results/455acb16');fs.mkdirSync(shots,{recursive:true});
const server=http.createServer((req,res)=>{
  let name;try{name=decodeURIComponent(new URL(req.url,'http://test.invalid').pathname);}catch{res.writeHead(400).end();return;}
  if(name.startsWith('/OLBG1/'))name=name.slice(6);
  let file=path.resolve(root,'.'+name);
  if(!file.startsWith(root+path.sep)){res.writeHead(403).end();return;}
  if(fs.existsSync(file)&&fs.statSync(file).isDirectory())file=path.join(file,'index.html');
  if(!fs.existsSync(file)){res.writeHead(404).end('Not found');return;}
  res.writeHead(200,{'Content-Type':({'.html':'text/html;charset=utf-8','.css':'text/css','.js':'text/javascript','.svg':'image/svg+xml','.json':'application/json','.csv':'text/csv'}[path.extname(file)]||'application/octet-stream')});
  fs.createReadStream(file).pipe(res);
});
(async()=>{
  const pkgDir=path.dirname(require.resolve('@sparticuz/chromium'));
  const pack=path.resolve(pkgDir,'../../bin/al2023.tar.br'),libDir=path.join(os.tmpdir(),'olbg455-browser-libs');
  fs.mkdirSync(libDir,{recursive:true});
  if(fs.existsSync(pack)&&!fs.existsSync(path.join(libDir,'lib/libnspr4.so'))){
    const result=cp.spawnSync('tar',['-xf','-','-C',libDir],{input:zlib.brotliDecompressSync(fs.readFileSync(pack))});assert.equal(result.status,0);
  }
  process.env.LD_LIBRARY_PATH=path.join(libDir,'lib')+(process.env.LD_LIBRARY_PATH?':'+process.env.LD_LIBRARY_PATH:'');
  await new Promise(r=>server.listen(0,'0.0.0.0',r));
  const base=`http://127.0.0.1:${server.address().port}/OLBG1/455acb16/`;
  let browser;
  try{
    browser=await chromium.launch({executablePath:await bundle.executablePath(),args:bundle.args.filter(x=>!['--single-process','--disable-web-security','--disable-site-isolation-trials'].includes(x)),headless:true});
    const ctx=await browser.newContext({viewport:{width:1480,height:1000},acceptDownloads:true});
    const p=await ctx.newPage(),errors=[],bad=[];
    p.on('pageerror',e=>errors.push(e.message));p.on('response',r=>{if(r.url().startsWith(base)&&r.status()>=400)bad.push(r.url());});
    await p.clock.install({time:new Date(desk.generated_at)});
    await p.goto(base,{waitUntil:'networkidle'});
    assert.equal(await p.locator('h1').textContent(),'The match research desk');
    assert.match(await p.locator('main').textContent(),/No supported High-confidence picks/);
    assert.ok(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));
    await p.screenshot({path:path.join(shots,'overview-desktop.png'),fullPage:true});
    await p.goto(base+'matches.html');
    assert.equal(await p.locator('[data-row]').count(),desk.counts.listings);
    assert.equal(await p.locator('[data-estimate]:visible').count(),desk.counts.priced_matches);
    await p.locator('.sport-filter').selectOption('tennis');
    assert.equal(await p.locator('[data-row]:visible').count(),desk.fixtures.filter(f=>f.sport==='tennis').length);
    await p.locator('.search').fill('Not-a-real-match-455');
    assert.equal(await p.locator('[data-row]:visible').count(),0);assert.ok(await p.locator('.no-results').isVisible());
    await p.locator('.reset').click();
    await p.locator('.price-filter').selectOption('priced');
    assert.equal(await p.locator('[data-row]:visible').count(),desk.counts.priced_matches);
    const price=p.locator('[data-odds]:visible').first();
    await p.locator('#odds-format').selectOption('decimal');assert.equal(await price.textContent(),await price.getAttribute('data-dec'));
    await p.locator('#odds-format').selectOption('american');assert.equal(await price.textContent(),await price.getAttribute('data-us'));
    const previous=await p.locator('[data-clock]').first().textContent();
    await p.locator('#timezone').selectOption('UTC');
    assert.notEqual(await p.locator('[data-clock]').first().textContent(),previous);
    const downloading=p.waitForEvent('download');await p.locator('.export').click();assert.match((await downloading).suggestedFilename(),/\.csv$/);
    await p.locator('.reset').click();await p.locator('.sort').click();
    assert.equal(await p.locator('th[aria-sort]').getAttribute('aria-sort'),'ascending');
    await p.goto(base+'verification.html#wta-ningbo-sf1');
    assert.ok(await p.locator('#wta-ningbo-sf1').evaluate(e=>e.open));
    assert.match(await p.locator('#wta-ningbo-sf1').textContent(),/Marie BOUZKOVA/);
    await p.goto(base+'sources.html#nhl-standings');assert.ok(await p.locator('#nhl-standings').evaluate(e=>e.open));
    await p.goto(base+'markets.html');
    assert.equal(await p.locator('[data-market-block]').count(),desk.counts.listings);
    await p.locator('#market-search').fill('nhl-2026020166');assert.equal(await p.locator('[data-market-block]:visible').count(),1);
    await p.goto(base+'matches.html');
    const deadline=desk.books.find(b=>b.fixture_id==='nhl-2026020166').expires_at;
    await p.clock.setFixedTime(new Date(Date.parse(deadline)+1));await p.reload();
    assert.equal(await p.locator('#nhl-2026020166 [data-estimate]:visible').count(),0);
    assert.ok(await p.locator('#expiry-alert').isVisible());
    // Fixture deadline is later for the other books; the first start alone must expire.
    assert.ok(await p.locator('[data-estimate]:visible').count()>0);
    await p.clock.setFixedTime(new Date(Date.parse(desk.observation_window.after)+6*3600_000));await p.reload();
    assert.equal(await p.locator('[data-estimate]:visible').count(),0);
    assert.ok((await p.locator('[data-estimate]').allTextContents()).every(t=>t===''));
    await ctx.close();
    const mobile=await browser.newContext({viewport:{width:390,height:844},isMobile:true});
    const mp=await mobile.newPage();await mp.clock.install({time:new Date(desk.generated_at)});
    await mp.goto(base);assert.ok(await mp.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),'Mobile page overflow');
    await mp.locator('.menu-button').click();assert.equal(await mp.locator('.menu-button').getAttribute('aria-expanded'),'true');
    await mp.keyboard.press('Escape');assert.equal(await mp.locator('.menu-button').getAttribute('aria-expanded'),'false');
    await mp.screenshot({path:path.join(shots,'overview-mobile.png'),fullPage:true});
    await mp.goto(base+'markets.html');assert.ok(await mp.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));
    await mobile.close();
    const nojs=await browser.newContext({javaScriptEnabled:false});const np=await nojs.newPage();
    await np.goto(base+'matches.html');assert.equal(await np.locator('[data-estimate]:visible').count(),0);
    assert.match(await np.locator('main').textContent(),/Estimates withheld without JavaScript/);
    assert.equal(await np.locator('[data-row]').count(),desk.counts.listings);await nojs.close();
    assert.deepEqual(errors,[]);assert.deepEqual(bad,[]);
    console.log('455acb16 Browser PASS: desktop/mobile, project prefix, search/reset/sport/priced filters, odds/timezone, sorting, CSV, evidence anchors, start/statistical freshness withholding and no-JS safety.');
  }finally{if(browser)await browser.close();await new Promise(r=>server.close(r));}
})().catch(e=>{console.error(e);process.exitCode=1;server.close();});
