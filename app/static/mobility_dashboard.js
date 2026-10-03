(() => {
  const state = { customerId: "CUST0001", data: null };
  const $ = (id) => document.getElementById(id);

  function setTheme() {
    const saved = localStorage.getItem("localiza-mobility-theme");
    if (saved === "dark") document.documentElement.setAttribute("data-theme", "dark");
    const button = $("themeToggle");
    if (!button) return;
    button.addEventListener("click", () => {
      const dark = document.documentElement.getAttribute("data-theme") === "dark";
      if (dark) {
        document.documentElement.removeAttribute("data-theme");
        localStorage.setItem("localiza-mobility-theme", "light");
        button.innerHTML = '<i class="bi bi-moon"></i>';
      } else {
        document.documentElement.setAttribute("data-theme", "dark");
        localStorage.setItem("localiza-mobility-theme", "dark");
        button.innerHTML = '<i class="bi bi-sun"></i>';
      }
    });
  }

  function openSidebar() {
    $("sidebar")?.classList.add("open");
    $("sidebarOverlay")?.classList.add("active");
  }
  function closeSidebar() {
    $("sidebar")?.classList.remove("open");
    $("sidebarOverlay")?.classList.remove("active");
  }

  function initials(name) {
    return String(name || "LC").split(/\s+/).slice(0, 2).map(v => v[0]).join("").toUpperCase();
  }

  function money(v) {
    return Number(v || 0).toLocaleString("pt-BR", { style: "currency", currency: "BRL", maximumFractionDigits: 0 });
  }

  function dateBR(v) {
    if (!v) return "—";
    const d = new Date(v);
    return Number.isNaN(d.getTime()) ? String(v) : d.toLocaleDateString("pt-BR");
  }

  function toast(message) {
    const el = $("toast");
    el.textContent = message;
    el.classList.add("show");
    clearTimeout(window.__toastTimer);
    window.__toastTimer = setTimeout(() => el.classList.remove("show"), 1900);
  }

  async function loadCustomers() {
    const response = await fetch("/api/customers?limit=500");
    const data = await response.json();
    const select = $("customerSelect");
    const unique = new Map();
    data.forEach(item => unique.set(item.customer_id, item));
    select.innerHTML = Array.from(unique.values()).map(item => `<option value="${item.customer_id}">${item.customer_id} · ${item.city}</option>`).join("");
    select.value = state.customerId;
    select.addEventListener("change", () => {
      state.customerId = select.value;
      loadDashboard();
    });
  }

  async function loadDashboard() {
    const response = await fetch(`/api/mobility-dashboard?customer_id=${encodeURIComponent(state.customerId)}`);
    if (!response.ok) throw new Error("Não foi possível carregar o dashboard.");
    state.data = await response.json();
    render();
  }

  function render() {
    const data = state.data;
    const client = data.customer || {};
    const vehicle = data.vehicle || {};
    const contract = data.contract || {};
    const telemetry = data.telemetry || {};
    const today = data.today || {};
    const planner = data.planner || {};

    const fullName = String(client.customer_id || state.customerId);
    $("customerAvatar").textContent = initials(fullName.replace("CUST", "Cliente "));
    $("customerName").textContent = fullName;
    $("customerLocation").textContent = `${client.profile ? String(client.profile).replaceAll("_", " ") : "Cliente"} · ${client.city || "—"}`;
    $("heroFirstName").textContent = fullName;
    $("heroDate").textContent = new Date().toLocaleDateString("pt-BR", { weekday: "long", day: "numeric", month: "long" });

    $("kpiKm").textContent = `${Number(telemetry.km_available || 0).toLocaleString("pt-BR")} km`;
    $("kpiKmMeta").textContent = `${Number(telemetry.franchise_utilization_pct || 0).toFixed(0)}% da franquia utilizada`;
    $("kpiMaintenance").textContent = `${Number(telemetry.maintenance_km_remaining || 0).toLocaleString("pt-BR")} km`;
    $("kpiMaintenanceMeta").textContent = "até a próxima manutenção";
    $("kpiContract").textContent = `${Number(contract.months_remaining || 0).toFixed(0)} meses`;
    $("kpiContractMeta").textContent = `renovação ${dateBR(contract.renewal_date)}`;
    $("kpiVehicle").textContent = `${vehicle.make || "—"} ${vehicle.model || ""}`.trim();
    $("kpiVehicleMeta").textContent = `${vehicle.year || "—"} · ${vehicle.powertrain || "—"}`;

    $("plannerStatus").textContent = planner.long_trip ? "viagem longa detectada" : "padrão de mobilidade";
    $("plannerOrigin").textContent = planner.origin || "—";
    $("plannerDestination").textContent = planner.destination || "—";
    $("plannerPurpose").textContent = planner.purpose || "mobilidade";
    $("plannerDistance").textContent = `${Number(planner.distance_km || 0).toFixed(0)} km`;
    $("plannerDate").textContent = planner.date ? `última saída relevante · ${dateBR(planner.date)}` : "sem saída recente";
    $("readinessValue").textContent = `${planner.readiness_score || 0}%`;
    const ring = $("readinessRing");
    ring.style.borderColor = planner.readiness_score >= 75 ? "var(--green-100)" : "var(--amber-light)";

    $("plannerChecks").innerHTML = (planner.checks || []).map(item => `
      <div class="check-item ${item.status}">
        <div class="check-icon"><i class="bi bi-${item.status === "ok" ? "check2" : "exclamation-lg"}"></i></div>
        <div class="check-copy"><span>${item.label}</span><small>${item.detail}</small></div>
      </div>`).join("");

    $("todayGreeting").textContent = data.assistant?.summary || "—";
    $("contextTitle").textContent = today.title || "—";
    $("contextDescription").textContent = today.description || "—";
    $("contextAction").innerHTML = `${today.action || "Abrir"} <i class="bi bi-arrow-right"></i>`;
    $("contextIcon").innerHTML = `<i class="bi bi-${today.icon || "stars"}"></i>`;

    const cx = data.context || {};
    const scoreMap = { high: 92, medium: 72, low: 54 };
    const priority = String(cx.context_priority || "low").toLowerCase();
    $("contextScore").textContent = `${scoreMap[priority] || 54}/100`;

    const signals = [
      ["KM", `${Number(telemetry.franchise_utilization_pct || 0).toFixed(0)}% usado`, Number(telemetry.franchise_utilization_pct || 0) >= 80 ? "high" : "low"],
      ["Manutenção", `${Number(telemetry.maintenance_km_remaining || 0).toFixed(0)} km`, Number(telemetry.maintenance_km_remaining || 0) <= 1000 ? "high" : "low"],
      ["Contrato", `${Number(contract.months_remaining || 0).toFixed(0)} meses`, Number(contract.months_remaining || 0) <= 3 ? "medium" : "low"],
      ["Benefício", cx.benefit_available ? "disponível" : "sem sinal", cx.benefit_available ? "medium" : "low"],
    ];
    $("signalList").innerHTML = signals.map(([label, value, level]) => `<div class="signal ${level}"><div class="signal-top"><strong>${label}</strong><span class="signal-dot"></span></div><span>${value}</span></div>`).join("");

    $("vehicleName").textContent = `${vehicle.make || "—"} ${vehicle.model || ""}`.trim();
    $("vehicleMeta").textContent = `${vehicle.version || "—"} · ${vehicle.powertrain || "—"}`;
    $("vehicleCity").textContent = telemetry.city_region || client.city || "—";
    $("routineList").innerHTML = (data.routine || []).length ? data.routine.map(row => `
      <div class="routine-row"><div><div class="routine-label">${row.label}</div><div class="routine-detail">${row.detail}</div></div><div class="confidence"><strong>${row.confidence}%</strong><small>confiança</small></div></div>`).join("") : '<div class="empty-state"><span>Ainda não há histórico suficiente para reconhecer sua rotina.</span></div>';

    $("fuelStatus").textContent = `${Number(telemetry.fuel_level_pct || 0).toFixed(0)}%`;
    $("usageStatus").textContent = `${Number(telemetry.franchise_utilization_pct || 0).toFixed(0)}%`;
    $("tripCountStatus").textContent = `${Number(telemetry.trip_count_30d || 0)}`;
    $("rangeStatus").textContent = `${Number(telemetry.estimated_range_km || 0).toFixed(0)} km`;

    const recs = data.assistant?.recent_recommendations || [];
    $("recommendationList").innerHTML = recs.length ? recs.map(rec => `
      <div class="recommendation-row"><div class="rec-icon"><i class="bi bi-${rec.recommendation_type === 'maintenance' ? 'tools' : rec.recommendation_type === 'benefit' ? 'gift' : 'stars'}"></i></div><div><strong>${rec.recommendation_text || 'Recomendação contextual'}</strong><span>${rec.need || 'Sinal identificado'}</span></div><small>${rec.action_label || 'Ver'}</small></div>`).join("") : '<div class="empty-state"><span>Nenhuma recomendação recente.</span></div>';
  }

  async function submitIntent(question) {
    const q = String(question || "").trim();
    if (!q) return;
    const response = await fetch(`/api/mobility-dashboard/intent?customer_id=${encodeURIComponent(state.customerId)}&q=${encodeURIComponent(q)}`);
    const result = await response.json();
    const action = result.action || {};
    $("intentResult").innerHTML = `<div class="result-card"><strong>${action.title || 'Próxima ação'}</strong><p>${action.description || ''}</p><div class="result-meta"><span class="result-intent">Intenção: ${result.intent || 'general'}</span><button class="primary-btn" type="button" data-toast="Ação conceitual selecionada">${action.action || 'Abrir'} <i class="bi bi-arrow-right"></i></button></div></div>`;
  }

  function bind() {
    $("mobileMenu")?.addEventListener("click", openSidebar);
    $("sidebarClose")?.addEventListener("click", closeSidebar);
    $("sidebarOverlay")?.addEventListener("click", closeSidebar);
    document.querySelectorAll(".sidebar-link").forEach(link => link.addEventListener("click", () => { if (window.innerWidth <= 800) closeSidebar(); }));
    document.addEventListener("click", (event) => {
      const el = event.target.closest("[data-toast]");
      if (el) toast(el.dataset.toast);
    });
    $("contextAction")?.addEventListener("click", () => toast(`Ação: ${state.data?.today?.action || 'abrir'}`));
    $("intentSubmit")?.addEventListener("click", () => submitIntent($("intentInput").value));
    $("intentInput")?.addEventListener("keydown", (event) => { if (event.key === "Enter") submitIntent($("intentInput").value); });
    document.querySelectorAll("[data-intent]").forEach(btn => btn.addEventListener("click", () => { $("intentInput").value = btn.dataset.intent; submitIntent(btn.dataset.intent); }));
    window.addEventListener("resize", () => { if (window.innerWidth > 800) closeSidebar(); });
  }

  async function init() {
    setTheme();
    bind();
    try {
      await loadCustomers();
      await loadDashboard();
    } catch (error) {
      console.error(error);
      toast("Não foi possível carregar o dashboard.");
    }
  }

  init();
})();
