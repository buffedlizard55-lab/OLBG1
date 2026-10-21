
function filt(){var q=document.getElementById('q').value.toLowerCase(),c=document.getElementById('cf').value,s=document.getElementById('sf')?document.getElementById('sf').value:'';
document.querySelectorAll('tbody tr').forEach(function(r){var ok=r.textContent.toLowerCase().includes(q);
if(c&&!r.dataset.conf.includes(c))ok=false; if(s&&r.dataset.sport!==s)ok=false; r.style.display=ok?'':'none';});}
