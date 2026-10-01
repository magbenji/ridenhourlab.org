// Live search/filter for the publications page (progressive enhancement).
(function(){
  var q=document.getElementById('pub-search'), t=document.getElementById('pub-type'), c=document.getElementById('pub-count');
  if(!q) return;
  var items=[].slice.call(document.querySelectorAll('.pub'));
  items.forEach(function(li){ li._html=li.innerHTML; li._text=li.textContent.toLowerCase(); });
  function esc(s){return s.replace(/[.*+?^${}()|[\]\\]/g,'\\$&');}
  function run(){
    var term=q.value.trim().toLowerCase(), type=t.value, n=0;
    var words=term.split(/\s+/).filter(Boolean);
    items.forEach(function(li){
      var ok=(!type||li.dataset.type===type)&&words.every(function(w){return li._text.indexOf(w)>-1||li.dataset.year===w;});
      li.hidden=!ok; if(ok) n++;
      li.innerHTML=li._html;
      if(ok&&words.length){
        var re=new RegExp('('+words.map(esc).join('|')+')','gi');
        [].forEach.call(li.querySelectorAll('.title,.authors,.venue'),function(el){
          el.innerHTML=el.innerHTML.replace(/(^|>)([^<]+)(?=<|$)/g,function(m,a,b){return a+b.replace(re,'<mark>$1</mark>');});
        });
      }
    });
    [].forEach.call(document.querySelectorAll('.year-group'),function(g){
      g.hidden=!g.querySelector('.pub:not([hidden])');
    });
    c.textContent=n+(n===1?' publication':' publications');
  }
  q.addEventListener('input',run); t.addEventListener('change',run);
  run();
})();
