
(function(){
  var btn=document.getElementById('menuBtn'),side=document.querySelector('.sidebar'),shade=document.getElementById('shade');
  if(btn&&side){btn.addEventListener('click',function(){var open=side.classList.toggle('open');btn.setAttribute('aria-expanded',open);if(shade)shade.hidden=!open;});}
  if(shade){shade.addEventListener('click',function(){side.classList.remove('open');shade.hidden=true;btn.setAttribute('aria-expanded',false);});}
  document.querySelectorAll('.filterbar').forEach(function(bar){
    var table=document.getElementById(bar.dataset.table);if(!table)return;
    var input=bar.querySelector('.rowfilter');var active='all';
    function apply(){var q=(input.value||'').toLowerCase();
      table.querySelectorAll('tbody tr').forEach(function(tr){
        var text=tr.textContent.toLowerCase();
        var grade=(tr.querySelector('.badge-high,.badge-med,.badge-low')||{}).textContent||'';
        var okText=!q||text.indexOf(q)>=0;var okFilter=active==='all'||grade.toLowerCase()===active;
        tr.style.display=(okText&&okFilter)?'':'none';});}
    if(input)input.addEventListener('input',apply);
    bar.querySelectorAll('.chip').forEach(function(chip){chip.addEventListener('click',function(){
      bar.querySelectorAll('.chip').forEach(function(c){c.classList.remove('active');});
      chip.classList.add('active');active=chip.dataset.filter;apply();});});
  });
})();
