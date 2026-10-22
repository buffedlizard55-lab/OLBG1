
document.addEventListener('DOMContentLoaded',()=>{
  document.querySelectorAll('[data-odds]').forEach(el=>{
    el.addEventListener('click',e=>{
      e.preventDefault();
      const fmt=e.target.dataset.odds;
      document.querySelectorAll('.odds').forEach(o=>{
        const v=o.dataset[fmt]; if(v) o.textContent=v;
      });
      document.querySelectorAll('[data-odds]').forEach(b=>b.classList.remove('on'));
      e.target.classList.add('on');
    });
  });
});
