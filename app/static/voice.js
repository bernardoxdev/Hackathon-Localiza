const querySource = new URLSearchParams(window.location.search).get('source');
const pathSource = window.location.pathname === '/reclame-aqui' ? 'reclameaqui' : window.location.pathname === '/app-store' ? 'appstore' : null;
const initialSource = querySource || pathSource;
const voiceState = { page: 1, pageSize: 12, source: ['all','googleplay','reclameaqui','appstore'].includes(initialSource) ? initialSource : 'all' };
const $ = (sel) => document.querySelector(sel);
const esc = (v) => String(v ?? '').replace(/[&<>'"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[c]));
const num = (v) => Number(v || 0).toLocaleString('pt-BR');
const pct = (v) => `${Number(v || 0).toLocaleString('pt-BR',{maximumFractionDigits:1})}%`;
async function api(path){ const r = await fetch(path); if(!r.ok) throw new Error(await r.text()); return r.json(); }

const labels = {
  source:{GOOGLE_PLAY:'Google Play',RECLAME_AQUI:'Reclame AQUI',APP_STORE:'Apple App Store'},
  sentiment:{positivo:'Positivo',negativo:'Negativo',neutro:'Neutro'},
  signal:{elogio:'Elogio',dor:'Dor',sugestao:'Sugestão',neutro:'Neutro'},
  urgency:{alta:'Alta',media:'Média',baixa:'Baixa'},
  topic:{
    pagamento_financeiro:'Financeiro / cobrança',
    contrato_assinatura:'Contrato / assinatura',
    telemetria_localizacao:'KM / telemetria',
    manutencao_agendamento:'Manutenção / agendamento',
    multas_condutor:'Multas / condutor',
    suporte_atendimento:'Suporte / atendimento',
    performance_estabilidade:'Performance / estabilidade',
    acesso_login:'Acesso / login',
    beneficios:'Benefícios',
    mobilidade_viagem:'Mobilidade / viagem',
    seguranca_privacidade:'Segurança / privacidade',
    entrega_veiculo:'Entrega / retirada',
    notificacoes:'Notificações',
    funcionalidade_usabilidade:'Funcionalidade / usabilidade',
    geral:'Experiência geral'
  },
  journey:{uso_do_app:'Uso do app',suporte:'Suporte',acesso:'Acesso',manutencao:'Manutenção',contrato:'Contrato',financeiro:'Financeiro',confianca:'Confiança',multas:'Multas',entrega:'Entrega',uso_do_carro:'Uso do carro',beneficios:'Benefícios',relacionamento:'Relacionamento',viagem:'Viagem'},
  opportunity:{
    zero_surpresa:'Zero Surpresa',proactive_care:'Proactive Care',support_prevention:'Prevenção de suporte',app_reliability:'Confiabilidade do app',beneficio_contextual:'Benefício contextual',notification_control:'Controle de notificações',mobility_planner:'Mobility Planner',security_trust:'Segurança e confiança',none:'Sem oportunidade'
  }
};
const label = (group,key) => labels[group]?.[key] || String(key ?? 'Não classificado').replaceAll('_',' ');

function kpis(summary){
  const n = summary.total || 1;
  const neg = summary.sentiment?.negativo || 0;
  const cards = [
    ['Sinais analisados', num(summary.total)],
    ['Dores', num(summary.voice_signal?.dor)],
    ['Sinais negativos', pct(neg/n*100)],
    ['Alta urgência', num(summary.high_urgency)],
    ['Com ação proposta', pct((summary.actionable||0)/n*100)],
  ];
  $('#voice-kpis').innerHTML = cards.map(([l,v]) => `<div class="kpi"><div class="label">${l}</div><div class="value">${v}</div></div>`).join('');
}

function sourceCards(summary){
  const rows = summary.sources || [];
  $('#voice-sources').innerHTML = rows.map(x => `<button class="source-card ${voiceState.source===x.source?'active':''}" data-source="${x.source}"><span>${label('source',x.source.toUpperCase())}</span><strong>${num(x.total)}</strong><small>${x.source==='googleplay'?'reviews públicas':x.source==='appstore'?'reviews públicas da App Store':'reclamações públicas pesquisadas'}</small></button>`).join('') + `<button class="source-card ${voiceState.source==='all'?'active':''}" data-source="all"><span>Todas</span><strong>${num(summary.total)}</strong><small>visão consolidada</small></button>`;
  document.querySelectorAll('.source-card').forEach(b => b.addEventListener('click', () => { voiceState.source = b.dataset.source; voiceState.page=1; loadAll(); }));
}

function signals(summary){
  const n = summary.total || 1;
  const entries = [
    ['negative','Negativo',summary.sentiment?.negativo||0],
    ['positive','Positivo',summary.sentiment?.positivo||0],
    ['','Dor',summary.voice_signal?.dor||0],
    ['','Sugestão',summary.voice_signal?.sugestao||0],
  ];
  $('#voice-signal-matrix').innerHTML = entries.map(([cls,name,count]) => `<div class="signal-card ${cls}"><div class="head"><span class="name">${name}</span><span class="count">${num(count)}</span></div><div class="share">${pct(count/n*100)} da base selecionada</div></div>`).join('');
}

function bars(el, rows, field){
  const items=(rows||[]).slice(0,8); const max=Math.max(...items.map(x=>Number(x.review_count ?? x.complaint_count)||0),1);
  el.innerHTML = items.length ? items.map(x => { const value=Number(x.review_count ?? x.complaint_count)||0; return `<div class="bar-row"><div class="bar-label">${esc(label(field==='topic'?'topic':field==='journey_moment'?'journey':'opportunity',x[field]))}</div><div class="bar-track"><div class="bar-fill" style="width:${(value/max*100).toFixed(1)}%"></div></div><div class="bar-value">${num(value)}</div></div>`; }).join('') : '<div class="muted">Sem dados.</div>';
}

function opportunities(summary){
  const items=(summary.opportunities||[]).filter(x=>x.context_opportunity!=='none').slice(0,8); const max=Math.max(...items.map(x=>Number(x.review_count)||0),1);
  $('#voice-opportunity-list').innerHTML=items.length?items.map(x=>`<div class="opp-row"><div class="opp-name">${esc(label('opportunity',x.context_opportunity))}</div><div class="opp-track"><div class="opp-fill" style="width:${(x.review_count/max*100).toFixed(1)}%"></div></div><div class="opp-value">${num(x.review_count)}</div></div>`).join(''):'<div class="muted">Nenhuma oportunidade classificada.</div>';
}

function funnel(summary){
  const topic = summary.topics?.[0];
  const pain = summary.pain_categories?.find(x => x.pain_category !== 'nenhuma');
  const opp = summary.opportunities?.find(x => x.context_opportunity !== 'none');
  const sourceLabel = voiceState.source === 'googleplay' ? 'Google Play' : voiceState.source === 'reclameaqui' ? 'Reclame AQUI' : voiceState.source === 'appstore' ? 'Apple App Store' : 'Google Play + Reclame AQUI + App Store';
  const cards = [
    ['01','Sinais',summary.total,sourceLabel],
    ['02','Tema recorrente',topic?.review_count || 0,label('topic',topic?.topic)],
    ['03','Dor',pain?.review_count || summary.voice_signal?.dor || 0,String(pain?.pain_category || 'fricção').replaceAll('_',' ')],
    ['04','Ação contextual',opp?.review_count || 0,label('opportunity',opp?.context_opportunity || 'none')]
  ];
  $('#voice-funnel').innerHTML = cards.map((c,i) => `<div class="funnel-card ${i<3?'arrow':''}"><div class="eyebrow2">${c[0]} · ${c[1]}</div><h4>${num(c[2])}</h4><p>${esc(c[3])}</p><div class="funnel-number">${i===0?'100%':pct(Number(c[2])/(summary.total||1)*100)}</div></div>`).join('');
}

function card(r){
  const high = r.urgency === 'alta';
  const source = r.source || 'GOOGLE_PLAY';
  const date = r.event_date ? new Date(r.event_date).toLocaleDateString('pt-BR') : '—';
  const title = source==='RECLAME_AQUI' ? r.title : source==='APP_STORE' ? (r.review_title || 'Review App Store') : `${r.rating || ''} estrelas`;
  const text = r.display_text || r.review_text || r.summary || '';
  return `<article class="review-card ${high?'high':''}">
    <div class="review-top"><div class="review-meta"><span class="review-tag">${esc(label('source',source))}</span><span class="review-tag ${r.sentiment==='negativo'?'danger':r.sentiment==='positivo'?'success':''}">${esc(label('sentiment',r.sentiment))}</span><span class="review-tag">${esc(label('topic',r.topic))}</span><span class="review-tag">${esc(label('journey',r.journey_moment))}</span>${high?'<span class="review-tag danger">Alta urgência</span>':''}</div><span class="review-id">${date} · ${esc(r.source_id)}</span></div>
    <div class="review-quote"><strong>${esc(title)}</strong><br>${esc(text)}</div>
    <div class="review-meta"><span class="review-tag">Dor: ${esc(String(r.pain_category||'nenhuma').replaceAll('_',' '))}</span><span class="review-tag">Oportunidade: ${esc(label('opportunity',r.context_opportunity))}</span>${r.status?`<span class="review-tag">Status: ${esc(r.status)}</span>`:''}</div>
    ${r.recommended_action && !String(r.recommended_action).toLowerCase().includes('nenhuma')?`<div class="review-action"><strong>Próxima ação:</strong> ${esc(r.recommended_action)}</div>`:''}
    ${r.source_url?`<div style="margin-top:10px"><a class="back-link" href="${esc(r.source_url)}" target="_blank" rel="noreferrer">Abrir fonte ↗</a></div>`:''}
  </article>`;
}

async function loadSummary(){
  const summary = await api(`/api/customer-voice/summary?source=${encodeURIComponent(voiceState.source)}`);
  kpis(summary); sourceCards(summary); signals(summary); opportunities(summary); funnel(summary);
  bars($('#voice-topics'), summary.topics, 'topic');
  bars($('#voice-journey'), summary.journey_moments, 'journey_moment');
}

function fill(id, values, group){
  const el=$(id), first=el.options[0]?.outerHTML || '<option value="">Todos</option>', old=el.value;
  el.innerHTML = first + (values||[]).map(v=>`<option value="${esc(v)}">${esc(label(group,v))}</option>`).join('');
  el.value = (values||[]).includes(old) ? old : '';
}

async function loadOptions(){
  const [g,r,a] = await Promise.all([api('/api/reviews/analysis?page=1&page_size=1'), api('/api/reclameaqui?page=1&page_size=1'), api('/api/appstore?page=1&page_size=1')]);
  const values = (a,b) => [...new Set([...(a||[]),...(b||[])])].sort();
  fill('#voice-sentiment', values(g.options?.sentiments,r.options?.sentiments,a.options?.sentiments), 'sentiment');
  fill('#voice-topic', values(g.options?.topics,r.options?.topics,a.options?.topics), 'topic');
  fill('#voice-urgency', values(g.options?.urgencies,r.options?.urgencies,a.options?.urgencies), 'urgency');
}

async function loadItems(){
  const p=new URLSearchParams({page:String(voiceState.page),page_size:String(voiceState.pageSize),source:voiceState.source});
  const q=$('#voice-search').value.trim(); const s=$('#voice-sentiment').value; const t=$('#voice-topic').value; const u=$('#voice-urgency').value;
  if(q)p.set('q',q); if(s)p.set('sentiment',s); if(t)p.set('topic',t); if(u)p.set('urgency',u);
  const data=await api(`/api/customer-voice?${p.toString()}`);
  $('#voice-review-list').innerHTML = data.rows?.length ? data.rows.map(card).join('') : '<div class="muted">Nenhum sinal encontrado com estes filtros.</div>';
  $('#voice-page-info').textContent = `Página ${data.page} de ${data.pages||1} · ${num(data.total)} sinais`;
  $('#voice-prev').disabled = data.page<=1; $('#voice-next').disabled = data.page>=(data.pages||1);
}

async function loadAll(){
  try{ await Promise.all([loadSummary(),loadItems()]); }catch(e){ console.error(e); $('#voice-review-list').innerHTML='<div class="muted">Não foi possível carregar a Voz do Cliente.</div>'; }
}

$('#voice-filter').addEventListener('click',()=>{voiceState.page=1;loadItems();});
$('#voice-clear').addEventListener('click',()=>{ $('#voice-search').value=''; $('#voice-sentiment').value=''; $('#voice-topic').value=''; $('#voice-urgency').value=''; voiceState.page=1; loadItems(); });
$('#voice-search').addEventListener('keydown',e=>{if(e.key==='Enter'){voiceState.page=1;loadItems();}});
$('#voice-prev').addEventListener('click',()=>{if(voiceState.page>1){voiceState.page--;loadItems();}});
$('#voice-next').addEventListener('click',()=>{voiceState.page++;loadItems();});
loadOptions().then(loadAll);
