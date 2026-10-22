/* Progressive enhancement only. All rows, source links and notes exist in HTML. */
(() => {
  'use strict';
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const menu = $('#menu-button'), sidebar = $('#sidebar'), shade = $('#sidebar-shade');
  function closeMenu() { sidebar?.classList.remove('open'); menu?.setAttribute('aria-expanded','false'); if(shade)shade.hidden=true; }
  menu?.addEventListener('click', () => { const open=!sidebar.classList.contains('open'); sidebar.classList.toggle('open',open);menu.setAttribute('aria-expanded',String(open));shade.hidden=!open; });
  shade?.addEventListener('click',closeMenu);
  document.addEventListener('keydown',e=>{if(e.key==='Escape'){closeMenu();menu?.focus();}});
  const form = $('#filters'), items = $$('[data-record]');
  const status = $('#result-count');
  function applyFilters() {
    if(!form)return;
    const query=($('#search',form)?.value||'').toLocaleLowerCase().trim();
    const sport=$('#sport-filter',form)?.value||'', state=$('#state-filter',form)?.value||'', day=$('#date-filter',form)?.value||'';
    const priced=$('#priced-only',form)?.checked||false;
    let visible=0;
    items.forEach(item=>{
      const show=(!query || (item.dataset.search||item.textContent).toLocaleLowerCase().includes(query))
        &&(!sport||item.dataset.sport===sport)&&(!state||item.dataset.state===state)&&(!day||item.dataset.date===day)
        &&(!priced||item.dataset.priced==='true');
      item.hidden=!show;if(show)visible++;
    });
    if(status)status.textContent=`${visible.toLocaleString()} of ${items.length.toLocaleString()} entries`;
    const empty=$('#no-results');if(empty)empty.hidden=visible!==0;
  }
  form?.addEventListener('input',applyFilters);form?.addEventListener('change',applyFilters);
  form?.addEventListener('submit',e=>e.preventDefault());
  $('#clear-filters')?.addEventListener('click',()=>{form.reset();applyFilters();$('#search')?.focus();});
  $$('[data-sort]').forEach(button=>button.addEventListener('click',()=>{
    const table=button.closest('table'),body=$('tbody',table),th=button.closest('th');
    const ascending=th.getAttribute('aria-sort')!=='ascending';
    $$('th[aria-sort]',table).forEach(x=>x.setAttribute('aria-sort','none'));
    th.setAttribute('aria-sort',ascending?'ascending':'descending');
    [...body.rows].sort((a,b)=>{const x=a.dataset[button.dataset.sort],y=b.dataset[button.dataset.sort];if(!x)return y?1:0;if(!y)return -1;return x.localeCompare(y)*(ascending?1:-1);}).forEach(row=>body.append(row));
  }));
  const format=$('#odds-format');
  function updateOdds(){
    const american=!format||format.value==='american';
    $$('[data-american]').forEach(el=>{if(el.dataset.expired!=='true')el.textContent=american?el.dataset.american:el.dataset.decimal;});
  }
  format?.addEventListener('change',updateOdds);
  function expire(now=Date.now()){
    const generated=Date.parse(document.body.dataset.snapshot||'');
    const globallyStale=Number.isFinite(generated)&&now-generated>6*3600*1000;
    let any=false;
    $$('[data-expires]').forEach(el=>{
      const deadline=Date.parse(el.dataset.expires),start=Date.parse(el.dataset.start||'');
      const priceDeadline=Date.parse(el.dataset.priceExpires||'');
      const priceExpired=Number.isFinite(priceDeadline)&&now>=priceDeadline;
      const fixtureExpired=(Number.isFinite(deadline)&&now>=deadline)||(Number.isFinite(start)&&now>=start);
      const invalid=fixtureExpired||priceExpired;
      if(!invalid)return;
      any=true;
      $$('[data-price-value]',el).forEach(price=>{price.textContent='';price.dataset.expired='true';price.removeAttribute('data-american');price.removeAttribute('data-decimal');});
      $$('[data-conf-value]',el).forEach(conf=>{conf.textContent='Withheld';conf.className='badge amber';});
      el.dataset.priced='false';
      // Expired statistical inputs withdraw the estimate, not the fixture's
      // independently supported future schedule or its evidence-state filter.
      if(fixtureExpired){
        const badge=$('[data-state-label]',el);if(badge){badge.textContent=now>=deadline?'Stale source':'Start elapsed';badge.className='badge amber';}
        el.dataset.state=now>=deadline?'stale':'start elapsed';
      }
      const cap=$('[data-expiry-reason]',el);if(cap)cap.hidden=false;
    });
    if(globallyStale||any){
      const alert=$('#expiry-alert');if(alert)alert.hidden=false;
      document.body.classList.add('snapshot-stale');
      const label=$('.freshness');if(label)label.textContent=globallyStale?'Snapshot stale':'Time checks updated';
      // Never leave a server-rendered "current" KPI frozen after expiry.
      $$('[data-live-kpi]').forEach(el=>{el.textContent='—';el.title='Snapshot count only; review refreshed time/status checks.';});
    }
    applyFilters();
  }
  expire();setInterval(expire,30000);
  // Open the evidence item addressed by a deep link, without requiring JS to read other rows.
  function openHash(){let id;try{id=decodeURIComponent(location.hash.slice(1));}catch{return;}const el=document.getElementById(id);if(el?.tagName==='DETAILS'){el.open=true;el.scrollIntoView({block:'start'});}}
  openHash();window.addEventListener('hashchange',openHash);
  // Download only visible rows as safe CSV; no browser calls to external APIs.
  $('#export-visible')?.addEventListener('click',()=>{
    const table=$('#match-table');if(!table)return;
    function safe(value){const s=value.trim().replace(/\s+/g,' ');return '"'+(/^[=+\-@\t\r]/.test(s)?"'"+s:s).replaceAll('"','""')+'"';}
    const lines=[[...table.tHead.rows[0].cells].map(c=>safe(c.textContent)).join(',')];
    [...table.tBodies[0].rows].filter(r=>!r.hidden).forEach(r=>lines.push([...r.cells].map(c=>safe(c.textContent)).join(',')));
    const url=URL.createObjectURL(new Blob(['\uFEFF'+lines.join('\r\n')],{type:'text/csv;charset=utf-8'}));
    const a=document.createElement('a');a.href=url;a.download='olbg-research-visible-rows.csv';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
  });
})();
