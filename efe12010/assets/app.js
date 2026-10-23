(function(){
  var menu=document.getElementById('menu'),side=document.getElementById('sidebar'),
      shade=document.getElementById('shade');
  function toggle(open){
    if(!side)return;
    side.classList.toggle('open',open);
    if(shade)shade.hidden=!open;
    if(menu)menu.setAttribute('aria-expanded',open?'true':'false');
  }
  if(menu)menu.addEventListener('click',function(){toggle(!side.classList.contains('open'));});
  if(shade)shade.addEventListener('click',function(){toggle(false);});
  document.addEventListener('keydown',function(ev){if(ev.key==='Escape')toggle(false);});

  // sortable tables
  Array.prototype.forEach.call(document.querySelectorAll('table.sortable'),function(tbl){
    var ths=tbl.querySelectorAll('thead th');
    Array.prototype.forEach.call(ths,function(th,idx){
      th.setAttribute('role','button');th.setAttribute('tabindex','0');
      function sort(){
        var body=tbl.tBodies[0],rows=Array.prototype.slice.call(body.rows),
            dir=th.getAttribute('data-dir')==='asc'?-1:1;
        Array.prototype.forEach.call(ths,function(o){o.removeAttribute('data-dir');});
        th.setAttribute('data-dir',dir===1?'asc':'desc');
        rows.sort(function(a,b){
          var x=(a.cells[idx]||{}).textContent||'',y=(b.cells[idx]||{}).textContent||'';
          var nx=parseFloat(x.replace(/[^0-9.+-]/g,'')),ny=parseFloat(y.replace(/[^0-9.+-]/g,''));
          if(!isNaN(nx)&&!isNaN(ny)&&x.replace(/[^0-9]/g,'')!==''&&y.replace(/[^0-9]/g,'')!=='')
            return (nx-ny)*dir;
          return x.trim().localeCompare(y.trim())*dir;
        });
        rows.forEach(function(r){body.appendChild(r);});
      }
      th.addEventListener('click',sort);
      th.addEventListener('keydown',function(ev){if(ev.key==='Enter'||ev.key===' '){ev.preventDefault();sort();}});
    });
  });

  // filter box + segmented state filter
  var q=document.getElementById('q'),seg=document.getElementById('seg'),mode='all';
  function apply(){
    var term=(q&&q.value||'').toLowerCase();
    Array.prototype.forEach.call(document.querySelectorAll('table.filterable tbody tr'),function(row){
      var text=row.textContent.toLowerCase(),show=true;
      if(term&&text.indexOf(term)===-1)show=false;
      if(show&&mode==='confirmed'&&text.indexOf('confirmed')===-1)show=false;
      if(show&&mode==='unconfirmed'&&text.indexOf('unconfirmed')===-1)show=false;
      if(show&&mode==='priced'&&row.querySelector('.odds')===null)show=false;
      if(show&&mode==='confirmed'&&text.indexOf('unconfirmed')!==-1)show=false;
      row.hidden=!show;
    });
  }
  if(q)q.addEventListener('input',apply);
  if(seg)seg.addEventListener('click',function(ev){
    var b=ev.target.closest('button');if(!b)return;
    Array.prototype.forEach.call(seg.querySelectorAll('button'),function(o){o.classList.remove('on');});
    b.classList.add('on');mode=b.getAttribute('data-f');apply();
  });
})();
