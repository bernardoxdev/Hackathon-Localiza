(async()=>{
  const M=window.MobilityPage;
  let customerId=null;
  let history=[];
  let baseToday={};

  function historyKey(id){return `localiza-assistant-history:${id}`;}
  function loadHistory(id){
    try{
      const raw=sessionStorage.getItem(historyKey(id));
      const parsed=raw?JSON.parse(raw):[];
      return Array.isArray(parsed)?parsed.slice(-20):[];
    }catch{return []}
  }
  function saveHistory(){
    if(!customerId)return;
    sessionStorage.setItem(historyKey(customerId),JSON.stringify(history.slice(-20)));
  }
  function escapeHtml(value){
    return String(value??"")
      .replaceAll("&","&amp;")
      .replaceAll("<","&lt;")
      .replaceAll(">","&gt;")
      .replaceAll('"',"&quot;")
      .replaceAll("'","&#039;");
  }
  function renderText(value){
    return escapeHtml(value).replaceAll("\n","<br>");
  }
  function addMessage(role,title,text){
    const win=document.getElementById('chatWindow');
    const wrap=document.createElement('div');
    wrap.className=`chat-message ${role}`;
    wrap.innerHTML=`<div class="chat-avatar"><i class="bi bi-${role==='assistant'?'stars':'person'}"></i></div><div><strong>${escapeHtml(title)}</strong><p>${renderText(text)}</p></div>`;
    win.appendChild(wrap);
    win.scrollTop=win.scrollHeight;
  }
  function addLoading(){
    const win=document.getElementById('chatWindow');
    const wrap=document.createElement('div');
    wrap.id='assistantLoading';
    wrap.className='chat-message assistant';
    wrap.innerHTML='<div class="chat-avatar"><i class="bi bi-stars"></i></div><div><strong>Assistente</strong><p>Consultando seu contexto...</p></div>';
    win.appendChild(wrap);
    win.scrollTop=win.scrollHeight;
  }
  function removeLoading(){document.getElementById('assistantLoading')?.remove();}
  function setStatus(engine){
    const pill=document.querySelector('.status-pill');
    const badge=document.querySelector('.data-badge');
    if(engine==='llm'){
      if(pill)pill.innerHTML='<span></span> IA contextual conectada';
      if(badge)badge.innerHTML='<i class="bi bi-stars"></i> IA conectada';
    }else{
      if(pill)pill.innerHTML='<span></span> Modo demonstração';
      if(badge)badge.innerHTML='<i class="bi bi-stars"></i> Fallback local';
    }
  }
  function setAction(action){
    if(!action)return;
    document.getElementById('assistantActionTitle').textContent=action.title||'Próxima ação';
    document.getElementById('assistantActionText').textContent=action.description||'—';
    document.getElementById('assistantActionBtn').textContent=action.label||'Abrir ação';
    document.getElementById('assistantActionBtn').dataset.actionType=action.type||'';
  }
  function restoreHistory(){
    if(!history.length)return;
    const win=document.getElementById('chatWindow');
    win.innerHTML='';
    history.forEach(item=>addMessage(item.role,item.role==='assistant'?'Assistente':'Você',item.content));
  }
  async function send(message){
    const q=String(message||'').trim();
    if(!q)return;
    const input=document.getElementById('assistantInput');
    const button=document.getElementById('assistantSend');
    if(input)input.value='';
    if(button)button.disabled=true;
    addMessage('user','Você',q);
    history.push({role:'user',content:q});
    saveHistory();
    addLoading();
    try{
      const response=await fetch('/api/assistant/message',{
        method:'POST',
        headers:{'Content-Type':'application/json'},
        body:JSON.stringify({customer_id:customerId,message:q,history:history.slice(-20,-1)})
      });
      const data=await response.json();
      removeLoading();
      if(!response.ok)throw new Error(data.detail||'Falha no assistente');
      addMessage('assistant','Assistente',data.message||'Não consegui formular uma resposta.');
      history.push({role:'assistant',content:data.message||''});
      saveHistory();
      setAction(data.action||null);
      setStatus(data.engine);
      if(data.notice)M.toast(data.notice);
    }catch(error){
      removeLoading();
      addMessage('assistant','Assistente',`Não consegui consultar o contexto agora. ${error.message||'Tente novamente.'}`);
      history.pop();
      saveHistory();
      M.toast('Falha ao consultar o assistente.');
    }finally{
      if(button)button.disabled=false;
      input?.focus();
    }
  }
  try{
    customerId=await M.loadCustomers();
    const data=await M.loadData(customerId);
    baseToday=data.today||{};
    M.hydrateShell(data);
    history=loadHistory(customerId);
    const c=data.customer||{},v=data.vehicle||{},t=data.telemetry||{},ct=data.contract||{};
    document.getElementById('assistantGreeting').textContent=data.assistant?.summary||'Posso ajudar a encontrar a próxima ação relevante.';
    const items=[
      ['Carro',`${v.make||''} ${v.model||''}`.trim()||'—'],
      ['KM',`${Number(t.franchise_utilization_pct||0).toFixed(0)}% da franquia usada`],
      ['Manutenção',`${Number(t.maintenance_km_remaining||0).toFixed(0)} km restantes`],
      ['Contrato',`${Number(ct.months_remaining||0).toFixed(0)} meses restantes`],
      ['Localização',String(c.consent_location).toLowerCase()==='true'?'permitida':'não compartilhada']
    ];
    document.getElementById('contextStack').innerHTML=items.map(x=>`<div class="context-item"><span>${escapeHtml(x[0])}</span><strong>${escapeHtml(x[1])}</strong></div>`).join('');
    setAction(baseToday);
    document.getElementById('assistantActionBtn').addEventListener('click',()=>M.toast(`Ação: ${document.getElementById('assistantActionBtn').dataset.actionType||baseToday.type||'abrir'}`));
    document.getElementById('assistantSend').addEventListener('click',()=>send(document.getElementById('assistantInput').value));
    document.getElementById('assistantInput').addEventListener('keydown',e=>{if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();send(e.target.value);}});
    document.querySelectorAll('[data-message]').forEach(b=>b.addEventListener('click',()=>send(b.dataset.message)));
    restoreHistory();
    const capability=await fetch('/api/assistant/capabilities').then(r=>r.ok?r.json():null).catch(()=>null);
    setStatus(capability?.llm_enabled?'llm':'fallback');
  }catch(e){
    console.error(e);
    M.toast('Não foi possível carregar o assistente.');
  }
})();
