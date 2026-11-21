/* Werewolf Academy interactive lesson. No external JS dependencies. */
'use strict';
(() => {
  const slides = [...document.querySelectorAll('.slide')];
  const claimData = JSON.parse(document.getElementById('claim-data').textContent);
  let current = 0;
  const $ = s => document.querySelector(s);
  const key = k => claimData[k];
  function showSlide(index) {
    current = Math.min(Math.max(index,0),slides.length-1);
    slides.forEach((slide,i) => {
      slide.classList.toggle('active',i===current);
      slide.setAttribute('aria-hidden',i!==current?'true':'false');
    });
    $('#slideCurrent').textContent=String(current+1).padStart(2,'0');
    $('#slideName').textContent=slides[current].dataset.title;
    $('#progressFill').style.width=`${100*(current+1)/slides.length}%`;
    $('#prevSlide').disabled=current===0;
    $('#nextSlide').disabled=current===slides.length-1;
    history.replaceState(null,'',`#slide-${current+1}`);
    window.scrollTo({top:0,behavior:'smooth'});
  }
  $('#prevSlide').addEventListener('click',()=>showSlide(current-1));
  $('#nextSlide').addEventListener('click',()=>showSlide(current+1));
  document.querySelectorAll('[data-next]').forEach(b=>b.addEventListener('click',()=>showSlide(current+1)));
  $('#restartDeck').addEventListener('click',()=>showSlide(0));
  $('#fullscreen').addEventListener('click',()=>{if(!document.fullscreenElement){document.documentElement.requestFullscreen?.()}else{document.exitFullscreen?.()}});
  document.addEventListener('keydown',e=>{
    if(['INPUT','SELECT','TEXTAREA'].includes(document.activeElement?.tagName))return;
    if(e.key==='ArrowRight'||e.key==='PageDown'){showSlide(current+1)}
    if(e.key==='ArrowLeft'||e.key==='PageUp'){showSlide(current-1)}
  });
  const requested=Number((location.hash.match(/^#slide-(\d+)$/)||[])[1]);
  showSlide(requested>=1&&requested<=10?requested-1:0);
  /* CSS flip: buttons stay keyboard-usable. */
  document.querySelectorAll('.role-card').forEach(card=>card.addEventListener('click',()=>{
    card.classList.toggle('flipped');card.setAttribute('aria-pressed',String(card.classList.contains('flipped')));
  }));
  /* Rules engine for the narrowly specified WKG12 example.
     Intentional simplification: ONE wolf attack and one optional poison target. */
  function evaluateNight(wolf,guard,previous,witch) {
    if(guard!=='none'&&guard===previous){return {valid:false,kind:'error',title:'守衛行動無效',detail:`守衛不能連續兩晚守護 ${guard} 號。請更換守護目標。`,citations:['guard_repeat']}}
    const hitGuard=wolf===guard;
    const usedHeal=witch==='heal';
    const doubleSave=hitGuard&&usedHeal;
    const wolfDies=doubleSave||(!hitGuard&&!usedHeal);
    const deaths=new Set();
    if(wolfDies)deaths.add(wolf);
    if(witch==='poison')deaths.add('9');
    const fragments=[];
    if(doubleSave)fragments.push(`${wolf} 號遭同守同救，仍然出局`);
    else if(wolfDies)fragments.push(`${wolf} 號遭狼刀出局`);
    else fragments.push(`${wolf} 號成功擋下狼刀`);
    if(witch==='poison')fragments.push(`9 號受到女巫毒藥影響，出局（即使受到守護也無效）`);
    return {
      valid:true,
      kind:deaths.size?'dead':'alive',
      title:doubleSave?`同守同救：${wolf} 號出局`:deaths.size?'夜晚有人出局':'平安夜！',
      detail:fragments.join('；')+'。',
      deaths:[...deaths],
      citations:doubleSave?['double_save']:witch==='poison'?['poison_unblockable']:['guard_repeat']
    };
  }
  function cite(keys){return keys.map(k=>`<a href="wiki/index.html#${key(k).id}" style="color:var(--gold)">${key(k).id} · ${key(k).source_ids.join(', ')}</a>`).join(' · ')}
  $('#runNight').addEventListener('click',()=>{
    const wolf=$('#wolfTarget').value,guard=$('#guardTarget').value,previous=$('#previousGuard').value,witch=$('#witchAction').value;
    const res=evaluateNight(wolf,guard,previous,witch);
    const out=$('#nightOutput');out.className=`sim-output result-${res.kind}`;
    const moon=res.kind==='error'?'⚠️':res.kind==='dead'?'🌑':'🌅';
    out.innerHTML=`<div class="moon-mini">${moon}</div><span class="faint-label">${res.valid?'DAWN RESULT':'ILLEGAL ACTION'}</span><h3>${res.title}</h3><p class="sim-status">${res.detail}</p><p>核對規則：${cite(res.citations)}</p>`;
  });
  $('#resetNight').addEventListener('click',()=>{
    $('#wolfTarget').value='6';$('#guardTarget').value='6';$('#previousGuard').value='none';$('#witchAction').value='heal';
    $('#nightOutput').className='sim-output';
    $('#nightOutput').innerHTML='<div class="moon-mini">☽</div><span class="faint-label">WAITING FOR DAWN</span><h3>夜晚尚未結束</h3><p>預設情境：6 號同時被狼人、守衛與女巫解藥選中。</p>';
  });
  const quizAnswers={q1:{answer:'b',rule:'double_save',explain:'同守同救仍出局。'},q2:{answer:'b',rule:'hunter_poison_shot',explain:'被女巫毒殺不能發動獵人技能。'},q3:{answer:'b',rule:'wolf_victory',explain:'本板採屠邊，不採人數追平。'}};
  $('#quiz').addEventListener('submit',e=>{
    e.preventDefault();const answers=new FormData(e.target);
    if(Object.keys(quizAnswers).some(q=>!answers.get(q))){$('#quizResult').textContent='請先回答三題，再提交。';return}
    let score=0;
    const details=Object.entries(quizAnswers).map(([q,obj],i)=>{
      const pass=answers.get(q)===obj.answer;if(pass)score++;
      return `<div><strong>${pass?'✓':'×'} Q${i+1}</strong>：${obj.explain} ${cite([obj.rule])}</div>`;
    });
    $('#quizResult').innerHTML=`<div class="score">${score} / 3</div>${details.join('')}`;
  });
  /* Exposes pure calculation to automated UI smoke testing. */
  window.WerewolfAcademy={evaluateNight,showSlide,getCurrent:()=>current,claimData};
})();
