from __future__ import annotations

import math
from functools import cache
from pathlib import Path
from typing import Any

import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "app" / "data"
STATIC_DIR = BASE_DIR / "app" / "static"
TEMPLATE_DIR = BASE_DIR / "app" / "templates"

app = FastAPI(
    title="RUPTURA 2026 — Case 2 Mobility Data Explorer",
    description="Dashboard conceitual para explorar datasets sintéticos e fontes públicas do protótipo Localiza Assinatura.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

DATASETS = {
    "vehicles": "vehicles.csv",
    "clients": "clients.csv",
    "contracts": "contracts.csv",
    "telemetry": "telemetry.csv",
    "trips": "trips.csv",
    "maintenance": "maintenance.csv",
    "app_events": "app_events.csv",
    "context_events": "context_events.csv",
    "recommendations": "recommendations.csv",
    "prototype_scenarios": "prototype_scenarios.csv",
    "data_dictionary": "data_dictionary.csv",
    "relationships": "relationships.csv",
    "insights_examples": "insights_examples.csv",
    "public_datasets": "public_datasets.csv",
}

DATASET_LABELS = {
    "vehicles": "Veículos",
    "clients": "Clientes",
    "contracts": "Contratos",
    "telemetry": "Telemetria",
    "trips": "Viagens",
    "maintenance": "Manutenção",
    "app_events": "Eventos do App",
    "context_events": "Contexto",
    "recommendations": "Recomendações",
    "prototype_scenarios": "Cenários do Protótipo",
    "data_dictionary": "Dicionário de Dados",
    "relationships": "Relacionamentos",
    "insights_examples": "Insights de Exemplo",
    "public_datasets": "Datasets Públicos",
}


def json_safe(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
        return None
    if isinstance(value, (pd.Timestamp,)):
        return value.isoformat()
    if hasattr(value, "item"):
        try:
            value = value.item()
        except Exception:
            pass
    if isinstance(value, (pd.Timestamp,)):
        return value.isoformat()
    if pd.isna(value) if not isinstance(value, (list, dict, tuple)) else False:
        return None
    return value


def records(df: pd.DataFrame) -> list[dict[str, Any]]:
    return [
        {k: json_safe(v) for k, v in row.items()}
        for row in df.to_dict(orient="records")
    ]


@cache
def load_dataset(name: str) -> pd.DataFrame:
    filename = DATASETS.get(name)
    if not filename:
        raise KeyError(name)
    path = DATA_DIR / filename
    if not path.exists():
        raise FileNotFoundError(path)
    df = pd.read_csv(path)
    return df


def dataset_or_404(name: str) -> pd.DataFrame:
    if name not in DATASETS:
        raise HTTPException(status_code=404, detail=f"Dataset desconhecido: {name}")
    return load_dataset(name)


def pct(v: float) -> float:
    return round(float(v), 1)


def latest_by(df: pd.DataFrame, key: str, date_col: str) -> pd.DataFrame:
    x = df.copy()
    x[date_col] = pd.to_datetime(x[date_col], errors="coerce")
    return x.sort_values(date_col).drop_duplicates(key, keep="last")


@app.get("/", include_in_schema=False)
def index() -> FileResponse:
    return FileResponse(TEMPLATE_DIR / "index.html")


@app.get("/api/health")
def health() -> dict[str, Any]:
    return {"status": "ok", "datasets": len(DATASETS)}


@app.get("/api/datasets")
def list_datasets() -> list[dict[str, Any]]:
    output = []
    for name, filename in DATASETS.items():
        df = load_dataset(name)
        output.append(
            {
                "name": name,
                "label": DATASET_LABELS.get(name, name),
                "rows": int(len(df)),
                "columns": int(len(df.columns)),
                "origin": sorted(
                    df["data_origin"].dropna().astype(str).unique().tolist()
                )
                if "data_origin" in df.columns
                else [],
                "filename": filename,
            }
        )
    return output


@app.get("/api/datasets/{name}")
def get_dataset(
    name: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
    q: str = Query(""),
) -> dict[str, Any]:
    df = dataset_or_404(name).copy()
    if q.strip():
        q = q.strip().lower()
        mask = pd.Series(False, index=df.index)
        for col in df.columns:
            mask = mask | df[col].astype(str).str.lower().str.contains(q, na=False)
        df = df.loc[mask]
    total = len(df)
    start = (page - 1) * page_size
    end = start + page_size
    page_df = df.iloc[start:end]
    return {
        "name": name,
        "label": DATASET_LABELS.get(name, name),
        "total": int(total),
        "page": page,
        "page_size": page_size,
        "columns": [{"name": c, "dtype": str(df[c].dtype)} for c in df.columns],
        "rows": records(page_df),
    }


@app.get("/api/summary")
def summary() -> dict[str, Any]:
    clients = load_dataset("clients")
    vehicles = load_dataset("vehicles")
    contracts = load_dataset("contracts")
    telemetry = load_dataset("telemetry")
    trips = load_dataset("trips")
    maint = load_dataset("maintenance")
    apps = load_dataset("app_events")
    contexts = load_dataset("context_events")
    recs = load_dataset("recommendations")

    active_contracts = contracts[
        contracts["status"].astype(str).str.lower().eq("active")
    ]
    redeemed = apps["benefit_redeemed"].fillna(False).astype(bool).sum()
    scheduled = apps["maintenance_scheduled"].fillna(False).astype(bool).sum()
    action_taken = recs["action_taken"].fillna(False).astype(bool).sum()

    return {
        "customers": int(len(clients)),
        "vehicles": int(len(vehicles)),
        "active_contracts": int(len(active_contracts)),
        "telemetry_records": int(len(telemetry)),
        "trips": int(len(trips)),
        "maintenance_records": int(len(maint)),
        "app_events": int(len(apps)),
        "context_events": int(len(contexts)),
        "recommendations": int(len(recs)),
        "benefit_redemptions": int(redeemed),
        "maintenance_schedules": int(scheduled),
        "recommendations_actioned": int(action_taken),
        "recommendation_action_rate": pct(action_taken / max(len(recs), 1) * 100),
        "origins": {
            "synthetic": int(
                sum(
                    (
                        "data_origin" in load_dataset(n).columns
                        and load_dataset(n)["data_origin"]
                        .astype(str)
                        .str.upper()
                        .eq("SYNTHETIC")
                        .any()
                    )
                    for n in DATASETS
                )
            ),
        },
    }


@app.get("/api/charts")
def charts() -> dict[str, Any]:
    clients = load_dataset("clients")
    vehicles = load_dataset("vehicles")
    contracts = load_dataset("contracts")
    apps = load_dataset("app_events")
    contexts = load_dataset("context_events")
    recs = load_dataset("recommendations")

    segment = clients["app_engagement_segment"].value_counts(dropna=False).to_dict()
    powertrain = vehicles["powertrain"].value_counts(dropna=False).to_dict()
    contract_status = contracts["status"].value_counts(dropna=False).to_dict()
    features = apps["feature"].value_counts().head(10).to_dict()
    context_priority = contexts["context_priority"].value_counts(dropna=False).to_dict()
    rec_types = recs["recommendation_type"].value_counts(dropna=False).to_dict()
    outcomes = recs["outcome"].value_counts(dropna=False).to_dict()

    return {
        "engagement_segment": segment,
        "powertrain": powertrain,
        "contract_status": contract_status,
        "app_features": features,
        "context_priority": context_priority,
        "recommendation_type": rec_types,
        "recommendation_outcomes": outcomes,
    }


@app.get("/api/customers")
def customer_options(
    q: str = Query(""), limit: int = Query(100, ge=1, le=500)
) -> list[dict[str, Any]]:
    df = load_dataset("clients")
    if q:
        mask = df.apply(
            lambda row: q.lower() in " ".join(map(str, row.tolist())).lower(), axis=1
        )
        df = df[mask]
    return records(
        df.head(limit)[
            [
                "customer_id",
                "profile",
                "city",
                "state",
                "region",
                "app_engagement_segment",
            ]
        ]
    )


@app.get("/api/customers/{customer_id}/360")
def customer_360(customer_id: str) -> dict[str, Any]:
    clients = load_dataset("clients")
    contracts = load_dataset("contracts")
    vehicles = load_dataset("vehicles")
    telemetry = load_dataset("telemetry")
    trips = load_dataset("trips")
    maint = load_dataset("maintenance")
    apps = load_dataset("app_events")
    contexts = load_dataset("context_events")
    recs = load_dataset("recommendations")

    client_rows = clients[clients.customer_id.eq(customer_id)]
    if client_rows.empty:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    client = client_rows.iloc[0].to_dict()
    cts = contracts[contracts.customer_id.eq(customer_id)].copy()
    vehicle_ids = cts.vehicle_id.astype(str).tolist()
    veh = vehicles[vehicles.vehicle_id.astype(str).isin(vehicle_ids)].copy()
    tel = telemetry[telemetry.customer_id.eq(customer_id)].copy()
    tlat = latest_by(tel, "vehicle_id", "timestamp") if not tel.empty else tel
    tr = trips[trips.customer_id.eq(customer_id)].copy()
    mt = maint[maint.customer_id.eq(customer_id)].copy()
    recent_maint = mt.sort_values("event_date", ascending=False).head(8)
    ae = (
        apps[apps.customer_id.eq(customer_id)]
        .copy()
        .sort_values("event_date", ascending=False)
        .head(10)
    )
    cx = (
        contexts[contexts.customer_id.eq(customer_id)]
        .copy()
        .sort_values("timestamp", ascending=False)
        .head(10)
    )
    rr = (
        recs[recs.customer_id.eq(customer_id)]
        .copy()
        .sort_values("generated_at", ascending=False)
        .head(10)
    )

    return {
        "client": {k: json_safe(v) for k, v in client.items()},
        "contracts": records(cts),
        "vehicles": records(veh),
        "latest_telemetry": records(tlat),
        "trips": records(tr),
        "maintenance": records(recent_maint),
        "app_events": records(ae),
        "context": records(cx),
        "recommendations": records(rr),
        "kpis": {
            "trip_count": int(len(tr)),
            "trip_km": round(float(tr["distance_km"].sum()), 1) if not tr.empty else 0,
            "app_events": int(len(apps[apps.customer_id.eq(customer_id)])),
            "maintenance_events": int(len(mt)),
            "recommendations": int(len(recs[recs.customer_id.eq(customer_id)])),
        },
    }


@app.get("/api/context-engine/{customer_id}")
def context_engine(customer_id: str) -> dict[str, Any]:
    cx = load_dataset("context_events")
    recs = load_dataset("recommendations")
    client_rows = cx[cx.customer_id.eq(customer_id)].copy()
    if client_rows.empty:
        raise HTTPException(
            status_code=404, detail="Contexto do cliente não encontrado"
        )
    client_rows["timestamp"] = pd.to_datetime(client_rows["timestamp"], errors="coerce")
    current = client_rows.sort_values("timestamp").iloc[-1]

    signals = []
    if float(current.get("franchise_utilization_pct", 0) or 0) >= 80:
        signals.append(
            {
                "type": "franquia",
                "severity": "high",
                "reason": f"{float(current['franchise_utilization_pct']):.1f}% utilizada",
                "action": "Ver KM",
            }
        )
    if bool(current.get("maintenance_soon", False)):
        signals.append(
            {
                "type": "manutenção",
                "severity": "high",
                "reason": f"{int(current.get('maintenance_km_remaining') or 0)} km restantes",
                "action": "Agendar revisão",
            }
        )
    if bool(current.get("contract_renewal_soon", False)):
        signals.append(
            {
                "type": "renovação",
                "severity": "medium",
                "reason": f"{int(current.get('contract_days_to_renewal') or 0)} dias",
                "action": "Revisar contrato",
            }
        )
    if bool(current.get("benefit_available", False)):
        signals.append(
            {
                "type": "benefício",
                "severity": "medium",
                "reason": "Há benefício contextual disponível",
                "action": "Ver benefício",
            }
        )
    if bool(current.get("long_trip_pattern", False)):
        signals.append(
            {
                "type": "viagem",
                "severity": "medium",
                "reason": "Padrão de viagens longas",
                "action": "Preparar viagem",
            }
        )
    if bool(current.get("low_energy", False)):
        signals.append(
            {
                "type": "energia",
                "severity": "high",
                "reason": "Nível de energia baixo",
                "action": "Localizar abastecimento/recarga",
            }
        )
    if bool(current.get("support_need_signal", False)):
        signals.append(
            {
                "type": "suporte",
                "severity": "high",
                "reason": "Sinal recente de necessidade de suporte",
                "action": "Resolver agora",
            }
        )

    signals.sort(key=lambda x: {"high": 0, "medium": 1, "low": 2}[x["severity"]])
    return {
        "customer_id": customer_id,
        "latest_context": {k: json_safe(v) for k, v in current.to_dict().items()},
        "signals": signals,
        "recommended_action": signals[0]["action"]
        if signals
        else "Nenhuma ação prioritária",
        "explanation": "Motor conceitual de protótipo: regras sintéticas, não regras da Localiza.",
        "recent_recommendations": records(
            recs[recs.customer_id.eq(customer_id)]
            .sort_values("generated_at", ascending=False)
            .head(10)
        ),
    }


@app.get("/api/metadata/{name}")
def metadata(name: str) -> dict[str, Any]:
    df = dataset_or_404(name)
    cols = []
    dictionary = load_dataset("data_dictionary")
    subset = (
        dictionary[dictionary.dataset.eq(name)]
        if "dataset" in dictionary.columns
        else pd.DataFrame()
    )
    for col in df.columns:
        row = subset[subset.column.eq(col)] if not subset.empty else pd.DataFrame()
        info = row.iloc[0].to_dict() if not row.empty else {}
        cols.append(
            {
                "name": col,
                "dtype": str(df[col].dtype),
                "type": info.get("type"),
                "unit": info.get("unit"),
                "origin": info.get("origin"),
                "description": info.get("description"),
            }
        )
    return {"name": name, "label": DATASET_LABELS.get(name, name), "columns": cols}
