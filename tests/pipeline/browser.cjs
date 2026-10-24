/* Browser contract tests for the public dashboard. Dependencies are pinned in the workflow. */
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),http=require('node:http'),os=require('node:os'),zlib=require('node:zlib'),cp=require('node:child_process');
const {chromium}=require('playwright-core'),bundle=require('@sparticuz/chromium');
const site=path.resolve(process.env.SITE_DIR||'_site');
const shots=path.resolve('.test-results');fs.mkdirSync(shots,{recursive:true});
const manifest=JSON.parse(fs.readFileSync(path.join(site,'data/desk/manifest.json'),'utf8'));
const desk=JSON.parse(fs.readFileSync(path.join(site,'data/desk/desk.json'),'utf8'));
const server=http.createServer((req,res)=>{
  let pathname;try{pathname=decodeURIComponent(new URL(req.url,'http://test.invalid').pathname);}catch{res.writeHead(400).end();return;}
  if(pathname.startsWith('/OLBG1/'))pathname=pathname.slice(6);
  let file=path.resolve(site,'.'+pathname);if(!file.startsWith(site+path.sep)&&file!==site){res.writeHead(403).end();return;}
  if(fs.existsSync(file)&&fs.statSync(file).isDirectory())file=path.join(file,'index.html');
  if(!fs.existsSync(file)){res.writeHead(404,{'Content-Type':'text/html'}).end(fs.readFileSync(path.join(site,'404.html')));return;}
  const types={'.html':'text/html; charset=utf-8','.css':'text/css','.js':'text/javascript','.json':'application/json','.csv':'text/csv','.svg':'image/svg+xml'};
  res.writeHead(200,{'Content-Type':types[path.extname(file)]||'application/octet-stream'});fs.createReadStream(file).pipe(res);
});
(async()=>{
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
    const context=await browser.newContext({viewport:{width:1400,height:1000},deviceScaleFactor:1});
    const page=await context.newPage();const errors=[],badResponses=[];
    page.on('pageerror',x=>errors.push(x.message));
    page.on('response',r=>{if(r.url().startsWith(base)&&r.status()>=400)badResponses.push(r.url());});

    await page.goto(base,{waitUntil:'networkidle'});
    assert.match(await page.title(),/OLBG Research Desk/);
    assert.equal((await page.locator('h1').textContent()).trim(),"Today's picks, and where they are");
    assert.equal(await page.locator('body').getAttribute('data-snapshot'),manifest.generated_at);
    await page.screenshot({path:path.join(shots,'dashboard-desktop.png'),fullPage:true});

    // The executive summary must lead with the high-confidence picks and count them honestly.
    const highRows=await page.locator('table').first().locator('tbody tr').count();
    assert.equal(highRows,desk.counts.high,'high-confidence table must show every high pick');
    assert.ok(await page.locator('.badge.high').count()>=desk.counts.high,'high badges missing');
    assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),'desktop overflow');

    // Every internally linked page must answer 200 and be registered in the manifest.
    for(const rel of manifest.pages){
      if(rel==='404.html') continue;
      await page.goto(base+rel,{waitUntil:'domcontentloaded'});
      assert.equal(await page.locator('h1').count(),1,rel+' must have exactly one h1');
      assert.equal(await page.locator('body').getAttribute('data-snapshot'),manifest.generated_at,rel+' lost the snapshot marker');
    }

    await page.goto(base+'picks.html',{waitUntil:'networkidle'});
    assert.equal(await page.locator('table').first().locator('tbody tr').count(),desk.counts.picks,'picks table row count');
    assert.equal(await page.locator('.badge.high').count()>=desk.counts.high,true,'picks page high badges');

    await page.goto(base+'predictions.html',{waitUntil:'networkidle'});
    assert.equal(await page.locator('article.article').count(),desk.counts.picks,'one article per pick');
    const bodies=await page.locator('article.article p.body').allTextContents();
    for(const text of bodies){
      assert.ok(text.trim().split(/\s+/).filter(Boolean).length>=30,'each prediction must clear 30 words');
      assert.ok(!/\b(model|verified|verification)\b/i.test(text),'internal vocabulary leaked into prose');
    }

    await page.goto(base+'matches.html',{waitUntil:'networkidle'});
    assert.equal(await page.locator('table').first().locator('tbody tr').count(),desk.counts.fixtures,'every fixture must be listed');

    await page.goto(base+'sports/ice-hockey.html',{waitUntil:'networkidle'});
    assert.ok(await page.locator('table').count()>=1,'priced sport page must carry its table');
    await page.goto(base+'sports/golf.html',{waitUntil:'networkidle'});
    assert.match(await page.locator('main').textContent(),/No match on this page/,'uncovered sport must say so plainly');
    assert.match(await page.locator('main').textContent(),/OLBG hub/,'uncovered sport must still point at the markets');

    // Mobile: no page-level horizontal overflow on the landing page or the widest table.
    const mobile=await context.newPage();
    await mobile.setViewportSize({width:390,height:844});
    for(const rel of ['index.html','picks.html','matches.html','predictions.html']){
      await mobile.goto(base+rel,{waitUntil:'networkidle'});
      assert.ok(await mobile.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),rel+' overflows on mobile');
    }
    await mobile.screenshot({path:path.join(shots,'dashboard-mobile.png'),fullPage:true});

    assert.deepEqual(errors,[],'page errors: '+errors.join(' | '));
    assert.deepEqual(badResponses,[],'bad responses: '+badResponses.join(' | '));
    console.log(`Browser gates passed: ${manifest.pages.length} pages, ${desk.counts.picks} picks, ${desk.counts.high} high.`);
  } finally {
    if(browser) await browser.close();
    server.close();
  }
})().catch(error=>{console.error(error);process.exit(1);});
