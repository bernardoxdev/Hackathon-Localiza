const API = '/api';
const state = { dataset: 'vehicles', page: 1, pageSize: 50, customer: 'CUST0001' };

const $ = (sel) => document.querySelector(sel);
const $$ = (sel) => [...document.querySelectorAll(sel)];
function esc(v){return String(v ?? '').replace(/[&<>'"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[c]));}
function money(v){return v==null?'—':new Intl.NumberFormat('pt-BR',{style:'currency',currency:'BRL',maximumFractionDigits:0}).format(Number(v));}
function num(v){return v==null?'—':new Intl.NumberFormat('pt-BR',{maximumFractionDigits:1}).format(Number(v));}
function showToast(msg){const t=$('#toast');t.textContent=msg;t.classList.add('show');setTimeout(()=>t.classList.remove('show'),2200)}
async function api(path){const r=await fetch(API+path);if(!r.ok){throw new Error(await r.text())};return r.json()}

function setView(view){$$('.view').forEach(x=>x.classList.toggle('active',x.id===view));$$('.nav-btn').forEach(b=>b.classList.toggle('active',b.dataset.view===view));}
$$('.nav-btn').forEach(b=>b.addEventListener('click',()=>setView(b.dataset.view)));

function renderBars(el, obj){
  const entries=Object.entries(obj||{}); if(!entries.length){el.innerHTML='<div class="muted">Sem dados.</div>';return;}
  const max=Math.max(...entries.map(([,v])=>Number(v)||0),1);
  el.innerHTML=entries.map(([k,v])=>`<div class="bar-row"><div class="bar-label">${esc(k)}</div><div class="bar-track"><div class="bar-fill" style="width:${(Number(v)/max*100).toFixed(1)}%"></div></div><div class="bar-value">${num(v)}</div></div>`).join('');
}

async function loadDashboard(){
  const [s,c]=await Promise.all([api('/summary'),api('/charts')]);
  const items=[['Clientes',s.customers],['Veículos',s.vehicles],['Telemetria',s.telemetry_records.toLocaleString('pt-BR')],['Viagens',s.trips.toLocaleString('pt-BR')],['Recomendações',s.recommendations.toLocaleString('pt-BR')],['Contratos ativos',s.active_contracts],['Eventos do app',s.app_events.toLocaleString('pt-BR')],['Contextos',s.context_events.toLocaleString('pt-BR')],['Ações de recomendação',s.recommendations_actioned.toLocaleString('pt-BR')],['Action rate',s.recommendation_action_rate+'%']];
  $('#kpis').innerHTML=items.map(([l,v])=>`<div class="kpi"><div class="label">${l}</div><div class="value">${v}</div></div>`).join('');
  renderBars($('#chart-engagement'),c.engagement_segment);renderBars($('#chart-powertrain'),c.powertrain);renderBars($('#chart-context'),c.context_priority);renderBars($('#chart-recommendations'),c.recommendation_type);
}

async function initDatasets(){
  const ds=await api('/datasets'); const opts=ds.map(d=>`<option value="${d.name}">${d.label} · ${d.rows.toLocaleString('pt-BR')} registros</option>`).join('');
  $('#dataset-select').innerHTML=opts; $('#dictionary-select').innerHTML=opts;
  $('#dataset-select').value=state.dataset; $('#dictionary-select').value=state.dataset;
  await loadDataset(); await loadDictionary();
}
async function loadDataset(){
  state.dataset=$('#dataset-select').value; const q=encodeURIComponent($('#dataset-search').value.trim());
  const d=await api(`/datasets/${state.dataset}?page=${state.page}&page_size=${state.pageSize}&q=${q}`);
  $('#dataset-info').textContent=`${d.total.toLocaleString('pt-BR')} registros`;
  $('#page-info').textContent=`Página ${d.page} · ${d.rows.length} registros`;
  const t=$('#data-table'); if(!d.rows.length){t.innerHTML='<tbody><tr><td>Sem resultados.</td></tr></tbody>';return}
  t.innerHTML=`<thead><tr>${d.columns.map(c=>`<th>${esc(c.name)}</th>`).join('')}</tr></thead><tbody>${d.rows.map(r=>`<tr>${d.columns.map(c=>`<td title="${esc(r[c.name])}">${esc(r[c.name])}</td>`).join('')}</tr>`).join('')}</tbody>`;
  await loadMeta(state.dataset);
}
async function loadMeta(name){const m=await api('/metadata/'+name);$('#dataset-meta').innerHTML=`<div class="meta-grid">${m.columns.map(c=>`<div class="meta-item"><strong>${esc(c.name)}</strong><div>${esc(c.description||'Sem descrição')}</div><div class="muted">tipo: ${esc(c.type||c.dtype)} · unidade: ${esc(c.unit||'—')} · origem: ${esc(c.origin||'—')}</div></div>`).join('')}</div>`}
$('#dataset-select').addEventListener('change',()=>{state.page=1;loadDataset()});$('#dataset-search-btn').addEventListener('click',()=>{state.page=1;loadDataset()});$('#dataset-search').addEventListener('keydown',e=>{if(e.key==='Enter'){state.page=1;loadDataset()}});$('#prev-page').addEventListener('click',()=>{if(state.page>1){state.page--;loadDataset()}});$('#next-page').addEventListener('click',()=>{state.page++;loadDataset()});

async function initCustomers(){const cs=await api('/customers?limit=500');const html=cs.map(c=>`<option value="${c.customer_id}">${c.customer_id} · ${c.city} · ${c.profile}</option>`).join('');$('#customer-select').innerHTML=html;$('#context-customer-select').innerHTML=html;$('#customer-select').value=state.customer;$('#context-customer-select').value=state.customer;await loadCustomer();await runContext();}
function kv(label,value){return `<div class="meta-item"><strong>${label}</strong><div>${esc(value)}</div></div>`}
async function loadCustomer(){const id=$('#customer-select').value;state.customer=id;const d=await api(`/customers/${id}/360`);const c=d.client;
  $('#customer-header').innerHTML=`<div class="customer-head">${kv('Cliente',c.customer_id)}${kv('Perfil',c.profile)}${kv('Cidade',c.city)}${kv('Segmento de app',c.app_engagement_segment)}</div>`;
  $('#customer-kpis').innerHTML=[['Viagens',d.kpis.trip_count],['KM de viagens',num(d.kpis.trip_km)],['Eventos app',d.kpis.app_events],['Manutenções',d.kpis.maintenance_events],['Recomendações',d.kpis.recommendations]].map(([l,v])=>`<div class="kpi"><div class="label">${l}</div><div class="value">${v}</div></div>`).join('');
  $('#customer-context').innerHTML=d.context.map(x=>`<div class="signal"><div class="top"><span>${esc(x.context_priority)} · ${esc(x.usage_segment)}</span><span>${esc(x.city)}</span></div><div class="muted">KM ${num(x.km_used_month)} · restante ${num(x.km_remaining)} · manutenção ${num(x.maintenance_km_remaining)} km · ${esc(x.timestamp)}</div></div>`).join('')||'<div class="muted">Sem contexto.</div>';
  $('#customer-recs').innerHTML=d.recommendations.map(x=>`<div class="signal"><div class="top"><span>${esc(x.recommendation_type)}</span><span>${esc(x.status)}</span></div><div>${esc(x.recommendation_text)}</div><div class="muted">Ação: ${esc(x.action_label)} · score ${num(x.context_score)}</div></div>`).join('')||'<div class="muted">Sem recomendações.</div>';
  $('#customer-telemetry').innerHTML=`<div class="table-wrap compact"><table>${simpleTable(d.latest_telemetry,['timestamp','km_used_month','monthly_km_allowance','km_available','franchise_utilization_pct','avg_speed_kmh','trip_count_30d','estimated_range_km','vehicle_status'])}</table></div>`;
  $('#customer-maintenance').innerHTML=`<div class="table-wrap compact"><table>${simpleTable(d.maintenance,['event_date','maintenance_type','maintenance_class','km_remaining','workshop_name','status','brake_status','oil_status'])}</table></div>`;
}
function simpleTable(rows,cols){if(!rows?.length)return '<tbody><tr><td>Sem dados.</td></tr></tbody>';return `<thead><tr>${cols.map(c=>`<th>${c}</th>`).join('')}</tr></thead><tbody>${rows.map(r=>`<tr>${cols.map(c=>`<td>${esc(r[c])}</td>`).join('')}</tr>`).join('')}</tbody>`}
$('#load-customer').addEventListener('click',()=>loadCustomer());

async function runContext(){const id=$('#context-customer-select').value;const d=await api('/context-engine/'+id);const ctx=d.latest_context;let html=`<div class="panel"><div class="meta-grid">${kv('Cliente',d.customer_id)}${kv('Cidade',ctx.city)}${kv('Uso da franquia',num(ctx.franchise_utilization_pct)+'%')}${kv('KM restantes',num(ctx.km_remaining))}${kv('Manutenção',num(ctx.maintenance_km_remaining)+' km')}${kv('Renovação',num(ctx.contract_days_to_renewal)+' dias')}${kv('Prioridade',ctx.context_priority)}${kv('Ação principal',d.recommended_action)}</div></div>`;
  html+=`<div class="grid-2"><div class="panel"><h3>Sinais detectados</h3>${d.signals.length?d.signals.map(s=>`<div class="signal ${s.severity}"><div class="top"><span>${esc(s.type)}</span><span>${esc(s.severity)}</span></div><div>${esc(s.reason)}</div><div class="muted">Ação: ${esc(s.action)}</div></div>`).join(''):'<div class="muted">Nenhum sinal prioritário.</div>'}</div><div class="panel"><h3>Decisão conceitual</h3><div class="signal"><div class="top"><span>Context Engine</span><span>regra sintética</span></div><p>O motor prioriza sinais de maior urgência e escolhe uma ação existente.</p><strong>${esc(d.recommended_action)}</strong><p class="muted">${esc(d.explanation)}</p></div></div></div>`;
  $('#context-result').innerHTML=html;
}
$('#run-context').addEventListener('click',runContext);

async function loadRecommendations(){const [c,d]=await Promise.all([api('/charts'),api('/datasets/recommendations?page=1&page_size=25')]);renderBars($('#rec-type-chart'),c.recommendation_type);renderBars($('#rec-outcome-chart'),c.recommendation_outcomes);const cols=['recommendation_id','customer_id','recommendation_type','recommendation_text','action_label','context_score','status','action_taken','outcome'];$('#rec-table').innerHTML=simpleTable(d.rows,cols)}
async function loadScenarios(){const d=await api('/datasets/prototype_scenarios?page=1&page_size=50');$('#scenario-grid').innerHTML=d.rows.map(s=>`<article class="scenario"><div class="pill">${esc(s.scenario_id)} · ${esc(s.profile)}</div><h3>${esc(s.need)}</h3><div class="muted">${esc(s.city)} · ${esc(s.vehicle)}</div><div class="flow"><div class="flow-box"><small>Contexto</small>${esc(s.context)}</div><div class="flow-box"><small>Necessidade</small>${esc(s.need)}</div><div class="flow-box"><small>Recomendação</small>${esc(s.recommendation)}</div><div class="flow-box"><small>Ação / valor</small>${esc(s.action)} · ${esc(s.value)}</div></div></article>`).join('')}
async function loadDictionary(){const name=$('#dictionary-select').value;const [meta,pub,rel]=await Promise.all([api('/metadata/'+name),api('/datasets/public_datasets?page=1&page_size=20'),api('/datasets/relationships?page=1&page_size=50')]);$('#dictionary-meta').innerHTML=`<div class="meta-grid">${meta.columns.map(c=>`<div class="meta-item"><strong>${esc(c.name)}</strong><div>${esc(c.description||'')}</div><div class="muted">${esc(c.type||c.dtype)} · ${esc(c.unit||'—')} · ${esc(c.origin||'—')}</div></div>`).join('')}</div>`;$('#public-datasets').innerHTML=pub.rows.map(r=>`<div class="signal"><div class="top"><span>${esc(r.dataset_name)}</span><span>${esc(r.origin)}</span></div><div>${esc(r.use_in_case)}</div><div class="muted">${esc(r.source)} · <a href="${esc(r.url)}" target="_blank" rel="noreferrer">fonte</a> · licença: ${esc(r.license)}</div><div class="muted">Limitações: ${esc(r.limitations)}</div></div>`).join('');$('#relationships-table').innerHTML=simpleTable(rel.rows,['parent_table','parent_key','child_table','child_key','cardinality','purpose'])}
$('#dictionary-select').addEventListener('change',loadDictionary);

Promise.all([loadDashboard(),initDatasets(),initCustomers(),loadRecommendations(),loadScenarios()]).catch(err=>{console.error(err);showToast('Erro ao carregar dados. Veja o console.');});
