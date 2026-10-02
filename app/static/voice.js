const voiceAPI = '/api';
const voiceState = {page:1,pageSize:10};

const V = (sel) => document.querySelector(sel);
function vEsc(v){return String(v ?? '').replace(/[&<>'"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[c]));}
function vPct(v){return `${Number(v || 0).toLocaleString('pt-BR',{maximumFractionDigits:1})}%`;}
function vNum(v){return Number(v || 0).toLocaleString('pt-BR');}
async function vApi(path){const r=await fetch(voiceAPI+path);if(!r.ok)throw new Error(await r.text());return r.json();}

const LABELS={
  sentiment:{positivo:'Positivo',negativo:'Negativo',neutro:'Neutro'},
  voice_signal:{elogio:'Elogio',dor:'Dor',sugestao:'Sugestão',neutro:'Neutro'},
  urgency:{alta:'Alta',media:'Média',baixa:'Baixa'},
  topic:{geral:'Experiência geral',performance_estabilidade:'Performance / estabilidade',funcionalidade_usabilidade:'Funcionalidade / usabilidade',suporte_atendimento:'Suporte / atendimento',acesso_login:'Acesso / login',manutencao_agendamento:'Manutenção / agendamento',contrato_assinatura:'Contrato / assinatura',pagamento_financeiro:'Pagamento / financeiro',seguranca_privacidade:'Segurança / privacidade',multas_condutor:'Multas / condutor',entrega_veiculo:'Entrega do veículo',telemetria_localizacao:'Telemetria / localização',beneficios:'Benefícios',notificacoes:'Notificações',mobilidade_viagem:'Mobilidade / viagem'},
  journey:{uso_do_app:'Uso do app',suporte:'Suporte',acesso:'Acesso',manutencao:'Manutenção',contrato:'Contrato',financeiro:'Financeiro',confianca:'Confiança',multas:'Multas',entrega:'Entrega',uso_do_carro:'Uso do carro',beneficios:'Benefícios',relacionamento:'Relacionamento',viagem:'Viagem'},
  opportunity:{none:'Sem oportunidade',app_reliability:'Confiabilidade do app',zero_surpresa:'Zero surpresa',support_prevention:'Prevenção de suporte',proactive_care:'Proactive Care',security_trust:'Segurança e confiança',beneficio_contextual:'Benefício contextual',notification_control:'Controle de notificações',mobility_planner:'Mobility Planner'}
};
function label(group,key){return LABELS[group]?.[key] || String(key ?? 'Não classificado').replaceAll('_',' ');}

function renderKpis(summary){
  const negative = summary.sentiment?.negativo || 0;
  const high = summary.high_urgency || 0;
  const cards=[
    ['Reviews analisadas',vNum(summary.total)],
    ['Dor identificada',vNum(summary.voice_signal?.dor)],
    ['Reviews negativas',vPct(negative/Math.max(summary.total,1)*100)],
    ['Alta urgência',vNum(high)],
    ['Com ação proposta',vPct(summary.actionable_rate_pct)]
  ];
  V('#voice-kpis').innerHTML=cards.map(([l,v])=>`<div class="kpi"><div class="label">${l}</div><div class="value">${v}</div></div>`).join('');
}

function renderSignalMatrix(summary){
  const total=summary.total||1;
  const entries=[['positive','Positivo',summary.sentiment?.positivo||0],['negative','Negativo',summary.sentiment?.negativo||0],['','Neutro',summary.sentiment?.neutro||0],['','Sugestões',summary.voice_signal?.sugestao||0]];
  V('#voice-signal-matrix').innerHTML=entries.map(([cls,name,count])=>`<div class="signal-card ${cls}"><div class="head"><span class="name">${name}</span><span class="count">${vNum(count)}</span></div><div class="share">${vPct(count/total*100)} das reviews</div></div>`).join('');
}

function renderOpportunities(rows){
  const items=(rows||[]).filter(x=>x["context_opportunity"]!=='none').slice(0,8);
  const max=Math.max(...items.map(x=>Number(x.review_count)||0),1);
  V('#voice-opportunity-list').innerHTML=items.length?items.map(x=>`<div class="opp-row"><div class="opp-name">${vEsc(label('opportunity',x.context_opportunity))}</div><div class="opp-track"><div class="opp-fill" style="width:${(x.review_count/max*100).toFixed(1)}%"></div></div><div class="opp-value">${vNum(x.review_count)}</div></div>`).join(''):'<div class="muted">Nenhuma oportunidade classificada.</div>';
}

function renderFunnel(summary){
  const topic = (summary.topics||[])[0];
  const pain = (summary.pain_categories||[]).find(x=>x.pain_category!=='nenhuma');
  const opp = (summary.opportunities||[]).find(x=>x.context_opportunity!=='none');
  const actionCount = summary.actionable || 0;
  const cards=[
    ['01','Sinal bruto',summary.total,'Reviews públicas'],
    ['02','Dor recorrente',pain?.review_count||summary.voice_signal?.dor||0,label('pain',pain?.pain_category||'dor')],
    ['03','Oportunidade',opp?.review_count||0,label('opportunity',opp?.context_opportunity||'none')],
    ['04','Ação',actionCount,'Reviews com ação classificada']
  ];
  V('#voice-funnel').innerHTML=cards.map((c,i)=>`<div class="funnel-card ${i<3?'arrow':''}"><div class="eyebrow2">${c[0]} · ${c[1]}</div><h4>${vNum(c[2])}</h4><p>${vEsc(c[3])}</p><div class="funnel-number">${i===0?'100%':vPct((Number(c[2])/(summary.total||1))*100)}</div></div>`).join('');
}

function renderBars(el, rows, field, group){
  const items=(rows||[]).slice(0,8); const max=Math.max(...items.map(x=>Number(x.review_count)||0),1);
  el.innerHTML=items.length?items.map(x=>`<div class="bar-row"><div class="bar-label" title="${vEsc(label(group,x[field]))}">${vEsc(label(group,x[field]))}</div><div class="bar-track"><div class="bar-fill" style="width:${(x.review_count/max*100).toFixed(1)}%"></div></div><div class="bar-value">${vNum(x.review_count)}</div></div>`).join(''):'<div class="muted">Sem dados.</div>';
}

function fillSelect(id, values, group){
  const el=V(id); const old=el.value; const opts=values.map(x=>`<option value="${vEsc(x)}">${vEsc(label(group,x))}</option>`).join('');
  const first=el.options[0]?.outerHTML || '<option value="">Todos</option>';
  el.innerHTML=first+opts; el.value=values.includes(old)?old:'';
}

function renderReviewCard(r){
  const high=r.urgency==='alta';
  const date=r.review_date ? new Date(r.review_date).toLocaleDateString('pt-BR') : '—';
  return `<article class="review-card ${high?'high':''}">
    <div class="review-top">
      <div class="review-meta">
        <span class="review-tag ${r.sentiment==='negativo'?'danger':r.sentiment==='positivo'?'success':''}">${vEsc(label('sentiment',r.sentiment))}</span>
        <span class="review-tag">${'★'.repeat(Math.max(1,Math.min(5,Number(r.rating)||0)))}</span>
        <span class="review-tag">${vEsc(label('topic',r.topic))}</span>
        <span class="review-tag">${vEsc(label('journey',r.journey_moment))}</span>
        ${high?'<span class="review-tag danger">Alta urgência</span>':''}
      </div>
      <span class="review-id">${date} · ${vEsc(r.review_id)}</span>
    </div>
    <div class="review-quote">“${vEsc(r.review_text)}”</div>
    <div class="review-meta">
      <span class="review-tag">Dor: ${vEsc(String(r.pain_category||'nenhuma').replaceAll('_',' '))}</span>
      <span class="review-tag">Oportunidade: ${vEsc(label('opportunity',r.context_opportunity))}</span>
    </div>
    ${r.recommended_action && r.recommended_action!=='nenhuma'?`<div class="review-action"><strong>Próxima ação:</strong> ${vEsc(r.recommended_action)}</div>`:''}
  </article>`;
}

async function loadVoice(){
  const [summary,insights]=await Promise.all([vApi('/reviews/analysis-summary'),vApi('/reviews/insights')]);
  renderKpis(summary);
  renderSignalMatrix(summary);
  renderOpportunities(summary.opportunities);
  renderFunnel(summary);
  renderBars(V('#voice-topics'),summary.topics,'topic','topic');
  renderBars(V('#voice-journey'),summary.journey_moments,'journey_moment','journey');
  fillSelect('#voice-sentiment',insights.sentiments || Object.keys(summary.sentiment||{}),'sentiment');
}

async function loadVoiceFilters(){
  const d=await vApi('/reviews/analysis?page=1&page_size=1');
  fillSelect('#voice-sentiment',d.options.sentiments,'sentiment');
  fillSelect('#voice-topic',d.options.topics,'topic');
  fillSelect('#voice-urgency',d.options.urgencies,'urgency');
  fillSelect('#voice-opportunity',d.options.context_opportunities,'opportunity');
}

async function loadVoiceReviews(){
  const p=new URLSearchParams({page:String(voiceState.page),page_size:String(voiceState.pageSize)});
  const q=V('#voice-search').value.trim(); const s=V('#voice-sentiment').value; const t=V('#voice-topic').value; const u=V('#voice-urgency').value; const o=V('#voice-opportunity').value;
  if(q)p.set('q',q); if(s)p.set('sentiment',s); if(t)p.set('topic',t); if(u)p.set('urgency',u); if(o)p.set('context_opportunity',o);
  const d=await vApi(`/reviews/analysis?${p.toString()}`);
  V('#voice-review-list').innerHTML=d.rows.length?d.rows.map(renderReviewCard).join(''):'<div class="muted">Nenhuma review encontrada com estes filtros.</div>';
  V('#voice-page-info').textContent=`Página ${d.page} de ${d.pages||1} · ${vNum(d.total)} reviews`;
  V('#voice-prev').disabled=d.page<=1; V('#voice-next').disabled=d.page>=(d.pages||1);
}

V('#voice-filter').addEventListener('click',()=>{voiceState.page=1;loadVoiceReviews();});
V('#voice-clear').addEventListener('click',()=>{V('#voice-search').value='';['#voice-sentiment','#voice-topic','#voice-urgency','#voice-opportunity'].forEach(s=>V(s).value='');voiceState.page=1;loadVoiceReviews();});
V('#voice-search').addEventListener('keydown',e=>{if(e.key==='Enter'){voiceState.page=1;loadVoiceReviews();}});
V('#voice-prev').addEventListener('click',()=>{if(voiceState.page>1){voiceState.page--;loadVoiceReviews();}});
V('#voice-next').addEventListener('click',()=>{voiceState.page++;loadVoiceReviews();});

Promise.all([loadVoice(),loadVoiceFilters(),loadVoiceReviews()]).catch(err=>{console.error(err);V('#voice-review-list').innerHTML='<div class="muted">Não foi possível carregar a análise das reviews.</div>';});
