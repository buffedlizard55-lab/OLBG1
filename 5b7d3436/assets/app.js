
(function(){
  const button=document.getElementById('menu-button');
  const nav=document.getElementById('primary-nav');
  if(button&&nav){button.addEventListener('click',function(){const open=nav.classList.toggle('open');button.setAttribute('aria-expanded',String(open));});}
  const now=Date.now();
  document.querySelectorAll('[data-price-expires]').forEach(function(el){
    const expiry=el.getAttribute('data-price-expires');
    const start=el.getAttribute('data-start');
    const expired=(expiry&&Date.parse(expiry)<=now)||(start&&Date.parse(start)<=now);
    if(expired){el.classList.add('is-expired');el.querySelectorAll('.expired-label').forEach(function(x){x.hidden=false;});}
  });
  const table=document.getElementById('filter-table');
  if(!table){return;}
  const rows=Array.from(table.tBodies[0].rows);
  const search=document.getElementById('source-search');
  const buttons=Array.from(document.querySelectorAll('[data-filter]'));
  const count=document.getElementById('filter-count');
  let active='all';
  function apply(){
    const q=(search&&search.value||'').trim().toLowerCase();let shown=0;
    rows.forEach(function(row){const kind=row.getAttribute('data-kind');const text=row.getAttribute('data-search')||row.textContent.toLowerCase();const visible=(active==='all'||kind===active)&&(!q||text.includes(q));row.hidden=!visible;if(visible){shown++;}});
    if(count){count.textContent=shown+' of '+rows.length+' rows';}
  }
  buttons.forEach(function(btn){btn.addEventListener('click',function(){active=btn.getAttribute('data-filter');buttons.forEach(function(b){b.classList.toggle('active',b===btn);});apply();});});
  if(search){search.addEventListener('input',apply);}apply();
})();
