/* Independent desk. No external calls, tracking, hidden data refresh or localhost backend. */
(() => {
'use strict';
const $=(s,r=document)=>r.querySelector(s), $$=(s,r=document)=>[...r.querySelectorAll(s)];
let timezone='America/Los_Angeles';
const generated=Date.parse(document.body.dataset.generated);
function day(d,z){return new Intl.DateTimeFormat('en-CA',{timeZone:z,year:'numeric',month:'2-digit',day:'2-digit'}).format(d);}
function expire(){
  let expired=false;
  $$('[data-estimate]').forEach(el=>{
    const deadline=Date.parse(el.dataset.deadline);
    if(!Number.isFinite(deadline)||Date.now()>=deadline){
      el.replaceChildren();el.hidden=true;
      if(el.nextElementSibling?.classList.contains('expired-value'))el.nextElementSibling.hidden=false;
      const row=el.closest('[data-row]');if(row)row.dataset.priced='false';expired=true;
    }
  });
  $$('[data-row]').forEach(row=>{
    const start=Date.parse(row.dataset.start),deadline=Date.parse(row.dataset.freshUntil);
    if((Number.isFinite(start)&&Date.now()>=start)||Date.now()>=deadline){
      row.dataset.state=Date.now()>=deadline?'stale':'start elapsed';
      const label=$('[data-state-label]',row);if(label)label.textContent=row.dataset.state;
    }
  });
  // Imports can be entirely stale even on pages without any price element.
  if(Date.now()>=Date.parse('2026-10-24T03:34:10Z'))expired=true;
  if(expired){const alert=$('#expiry-alert');if(alert)alert.hidden=false;}
  $$('.filter-section').forEach(filterSection);
}
function clocks(){
  $$('[data-clock]').forEach(el=>{
    const date=new Date(el.dataset.clock);
    el.textContent=new Intl.DateTimeFormat('en-US',{timeZone:timezone,month:'short',day:'numeric',hour:'numeric',minute:'2-digit',timeZoneName:'short'}).format(date);
    el.title=el.dataset.clock;
  });
}
function odds(){
  const format=$('#odds-format')?.value||'american';
  $$('[data-odds]').forEach(el=>{el.textContent=format==='decimal'?el.dataset.dec:el.dataset.us;});
}
function filterSection(section){
  const search=($('.search',section)?.value||'').trim().toLowerCase();
  const sport=$('.sport-filter',section)?.value||'';
  const state=$('.state-filter',section)?.value||'';
  const priced=$('.price-filter',section)?.value||'';
  let n=0;
  $$('[data-row]',section).forEach(row=>{
    const stateMatch=!state||(state==='calendar'?/calendar|status unverified/.test(row.dataset.state):row.dataset.state.includes(state));
    row.hidden=!!((search&&!row.textContent.toLowerCase().includes(search))||(sport&&row.dataset.sport!==sport)||!stateMatch||(priced&&row.dataset.priced!=='true'));
    if(!row.hidden)n++;
  });
  const empty=$('.no-results',section);if(empty)empty.hidden=n!==0;
  const count=$('.filter-count',section);if(count)count.textContent=n+' rows';
}
function exportCSV(section){
  const table=$('table',section);if(!table)return;
  // Guard against formula execution when users open exports in spreadsheets.
  const cell=s=>{s=s.replace(/\s+/g,' ').trim();if(/^[=+@-]/.test(s))s="'"+s;return '"'+s.replace(/"/g,'""')+'"';};
  const rows=$$('tr',table).filter(r=>!r.hidden).map(row=>$$('th,td',row).map(td=>cell(td.innerText)).join(','));
  const blob=new Blob(['\ufeff'+rows.join('\r\n')],{type:'text/csv;charset=utf-8'});
  const link=document.createElement('a');link.href=URL.createObjectURL(blob);link.download='455acb16-visible-as-of.csv';document.body.append(link);link.click();link.remove();setTimeout(()=>URL.revokeObjectURL(link.href),1000);
}
$$('.filter-section').forEach(section=>{
  $$('input,select',section).forEach(el=>el.addEventListener('input',()=>filterSection(section)));
  $('.reset',section)?.addEventListener('click',()=>{$$('input,select',section).forEach(el=>{el.value='';});filterSection(section);});
  $('.export',section)?.addEventListener('click',()=>exportCSV(section));
  $('.sort',section)?.addEventListener('click',event=>{
    const tbody=$('tbody',section),ascending=event.currentTarget.dataset.direction!=='ascending';
    event.currentTarget.dataset.direction=ascending?'ascending':'descending';
    event.currentTarget.closest('th').setAttribute('aria-sort',ascending?'ascending':'descending');
    const value=r=>r.dataset.start||'9999';
    $$('[data-row]',section).sort((a,b)=>value(a).localeCompare(value(b))*(ascending?1:-1)).forEach(r=>tbody.append(r));
  });
  filterSection(section);
});
$('#timezone')?.addEventListener('change',event=>{timezone=event.target.value;clocks();});
$('#odds-format')?.addEventListener('change',odds);
$('#market-search')?.addEventListener('input',event=>{
  const term=event.target.value.toLowerCase().trim();$$('[data-market-block]').forEach(b=>{b.hidden=!!(term&&!b.textContent.toLowerCase().includes(term));});
});
$('.menu-button')?.addEventListener('click',event=>{
  const button=event.currentTarget,open=button.getAttribute('aria-expanded')!=='true';
  button.setAttribute('aria-expanded',String(open));$('#sidebar')?.classList.toggle('open',open);
});
document.addEventListener('keydown',event=>{if(event.key==='Escape'){$('#sidebar')?.classList.remove('open');$('.menu-button')?.setAttribute('aria-expanded','false');}});
function openHash(){try{const item=document.getElementById(decodeURIComponent(location.hash.slice(1)));if(item?.tagName==='DETAILS')item.open=true;}catch{}}
window.addEventListener('hashchange',openHash);openHash();
// Withhold first, then reveal only values whose deadline has passed the check.
expire();clocks();odds();document.documentElement.classList.add('js-ready');
setInterval(expire,15000);
})();
