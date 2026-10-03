(() => {
  const $ = (id) => document.getElementById(id);
  function initials(name){return String(name||"LC").split(/\s+/).slice(0,2).map(v=>v[0]).join("").toUpperCase();}
  function toast(message){const el=$("toast");if(!el)return;el.textContent=message;el.classList.add("show");clearTimeout(window.__toastTimer);window.__toastTimer=setTimeout(()=>el.classList.remove("show"),1800);}
  function setTheme(){const saved=localStorage.getItem("localiza-mobility-theme")||"light";if(saved==="dark"){document.documentElement.setAttribute("data-theme","dark");if($("themeToggle"))$("themeToggle").innerHTML='<i class="bi bi-sun"></i>';}else if($("themeToggle"))$("themeToggle").innerHTML='<i class="bi bi-moon"></i>';}
  function bindShell(){
    $("mobileMenu")?.addEventListener("click",()=>{$("sidebar")?.classList.add("open");$("sidebarOverlay")?.classList.add("active");});
    $("sidebarClose")?.addEventListener("click",()=>{$("sidebar")?.classList.remove("open");$("sidebarOverlay")?.classList.remove("active");});
    $("sidebarOverlay")?.addEventListener("click",()=>{$("sidebar")?.classList.remove("open");$("sidebarOverlay")?.classList.remove("active");});
    $("themeToggle")?.addEventListener("click",()=>{const dark=document.documentElement.getAttribute("data-theme")==="dark";if(dark){document.documentElement.removeAttribute("data-theme");localStorage.setItem("localiza-mobility-theme","light");$("themeToggle").innerHTML='<i class="bi bi-moon"></i>';}else{document.documentElement.setAttribute("data-theme","dark");localStorage.setItem("localiza-mobility-theme","dark");$("themeToggle").innerHTML='<i class="bi bi-sun"></i>';} });
    document.addEventListener("click",e=>{const el=e.target.closest("[data-toast]");if(el)toast(el.dataset.toast);});
  }
  async function loadCustomers(){
    const res=await fetch('/api/customers?limit=500'); if(!res.ok) return null; const rows=await res.json(); const select=$("customerSelect"); if(!select)return null;
    const params=new URLSearchParams(location.search); const chosen=params.get('customer_id')||localStorage.getItem('localiza-customer-id')||'CUST0001';
    const unique=[];const seen=new Set();rows.forEach(r=>{if(!seen.has(r.customer_id)){seen.add(r.customer_id);unique.push(r);}});
    select.innerHTML=unique.map(r=>`<option value="${r.customer_id}">${r.customer_id} · ${r.city||''}</option>`).join('');select.value=seen.has(chosen)?chosen:(unique[0]?.customer_id||'CUST0001');
    localStorage.setItem('localiza-customer-id',select.value);
    select.addEventListener('change',()=>{localStorage.setItem('localiza-customer-id',select.value);location.search='?customer_id='+encodeURIComponent(select.value);});
    return select.value;
  }
  async function loadData(customerId){const r=await fetch(`/api/mobility-dashboard?customer_id=${encodeURIComponent(customerId)}`);if(!r.ok)throw new Error('Falha ao carregar contexto');return r.json();}
  function hydrateShell(data){const c=data.customer||{};if($("customerAvatar"))$("customerAvatar").textContent=initials(c.customer_id||'Cliente');if($("customerName"))$("customerName").textContent=c.customer_id||'Cliente';if($("customerLocation"))$("customerLocation").textContent=`${String(c.profile||'cliente').replaceAll('_',' ')} · ${c.city||'—'}`;if($("heroDate"))$("heroDate").textContent=new Date().toLocaleDateString('pt-BR',{weekday:'long',day:'numeric',month:'long'});}
  window.MobilityPage={$,toast,setTheme,bindShell,loadCustomers,loadData,hydrateShell};
  setTheme();bindShell();
})();
