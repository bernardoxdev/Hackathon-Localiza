from __future__ import annotations

from typing import Any

import pandas as pd
from fastapi import APIRouter

from app.core.data import DATASETS, load_dataset, pct

router = APIRouter(prefix="/api", tags=["Analytics"])


@router.get("/summary")
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
    reviews = load_dataset("googleplay_reviews")

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
        "googleplay_reviews": int(len(reviews)),
        "googleplay_average_rating": (
            round(
                float(pd.to_numeric(reviews["rating"], errors="coerce").mean()),
                2,
            )
            if not reviews.empty
            else 0.0
        ),
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


@router.get("/charts")
def charts() -> dict[str, Any]:
    clients = load_dataset("clients")
    vehicles = load_dataset("vehicles")
    contracts = load_dataset("contracts")
    apps = load_dataset("app_events")
    contexts = load_dataset("context_events")
    recs = load_dataset("recommendations")

    return {
        "engagement_segment": clients["app_engagement_segment"]
        .value_counts(dropna=False)
        .to_dict(),
        "powertrain": vehicles["powertrain"].value_counts(dropna=False).to_dict(),
        "contract_status": contracts["status"].value_counts(dropna=False).to_dict(),
        "app_features": apps["feature"].value_counts().head(10).to_dict(),
        "context_priority": contexts["context_priority"]
        .value_counts(dropna=False)
        .to_dict(),
        "recommendation_type": recs["recommendation_type"]
        .value_counts(dropna=False)
        .to_dict(),
        "recommendation_outcomes": recs["outcome"].value_counts(dropna=False).to_dict(),
    }
