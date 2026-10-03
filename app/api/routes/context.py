from __future__ import annotations

from typing import Any

import pandas as pd
from fastapi import APIRouter, HTTPException

from app.core.data import json_safe, load_dataset, records

router = APIRouter(prefix="/api/context-engine", tags=["Context Engine"])


@router.get("/{customer_id}")
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
