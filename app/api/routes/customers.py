from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Query

from app.core.data import json_safe, latest_by, load_dataset, records

router = APIRouter(prefix="/api/customers", tags=["Customers"])


@router.get("")
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


@router.get("/{customer_id}/360")
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
