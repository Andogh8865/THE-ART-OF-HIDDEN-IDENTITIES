'use strict';
(()=>{
 const search=document.getElementById('wikiSearch');
 const cards=[...document.querySelectorAll('.wiki-entry')];
 const topics=[...document.querySelectorAll('.topic')];
 search.addEventListener('input',()=>{
   const term=search.value.trim().toLowerCase();
   let shown=0;
   cards.forEach(card=>{const match=card.dataset.search.toLowerCase().includes(term);card.classList.toggle('hidden',!match);if(match)shown++});
   topics.forEach(topic=>{if(topic.id==='conflicts'||topic.id==='sources')return;topic.classList.toggle('hidden',!topic.querySelector('.wiki-entry:not(.hidden)'))});
   document.getElementById('wikiCount').textContent=`顯示 ${shown} / ${cards.length} 條規則`;
 });
})();
