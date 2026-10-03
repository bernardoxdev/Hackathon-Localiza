from __future__ import annotations

from typing import Any

import pandas as pd

from app.core.data import json_safe, load_dataset, records

DAY_PT = {
    "Monday": "segunda",
    "Tuesday": "terça",
    "Wednesday": "quarta",
    "Thursday": "quinta",
    "Friday": "sexta",
    "Saturday": "sábado",
    "Sunday": "domingo",
}

INTENT_RULES = {
    "maintenance": [
        "revisão",
        "revisao",
        "manutenção",
        "manutencao",
        "oficina",
        "pneu",
        "óleo",
        "oleo",
    ],
    "km": ["km", "quilometr", "franquia", "rodar"],
    "trip": ["viajar", "viagem", "estrada", "rota", "planejar", "planejar viagem"],
    "benefit": ["benefício", "beneficio", "desconto", "clube", "parceiro"],
    "contract": ["contrato", "assinatura", "renov", "vencimento"],
    "support": ["ajuda", "problema", "suporte", "assistência", "assistencia"],
}


def _latest(df: pd.DataFrame, key: str, date_col: str) -> pd.DataFrame:
    if df.empty:
        return df
    x = df.copy()
    x[date_col] = pd.to_datetime(x[date_col], errors="coerce")
    return x.sort_values(date_col).drop_duplicates(key, keep="last")


def _first_or_empty(df: pd.DataFrame) -> dict[str, Any]:
    if df.empty:
        return {}
    return {k: json_safe(v) for k, v in df.iloc[0].to_dict().items()}


def _choose_action(
    context: pd.Series, telemetry: pd.Series, contract: pd.Series
) -> dict[str, Any]:
    utilization = float(
        context.get(
            "franchise_utilization_pct", telemetry.get("franchise_utilization_pct", 0)
        )
        or 0
    )
    maintenance = (
        bool(context.get("maintenance_soon", False))
        or float(
            context.get(
                "maintenance_km_remaining",
                telemetry.get("maintenance_km_remaining", 99999),
            )
            or 99999
        )
        <= 1000
    )
    renewal = (
        bool(context.get("contract_renewal_soon", False))
        or float(contract.get("months_remaining", 999)) <= 3
    )
    benefit = bool(context.get("benefit_available", False))
    long_trip = bool(context.get("long_trip_pattern", False))
    low_energy = (
        bool(context.get("low_energy", False))
        or float(telemetry.get("fuel_level_pct", 100) or 100) <= 20
    )

    if maintenance:
        return {
            "type": "maintenance",
            "title": "Sua revisão está próxima",
            "description": f"Restam cerca de {int(float(context.get('maintenance_km_remaining', telemetry.get('maintenance_km_remaining', 0)) or 0))} km para a próxima manutenção.",
            "action": "Agendar revisão",
            "tone": "attention",
            "icon": "wrench",
        }
    if utilization >= 80:
        return {
            "type": "km",
            "title": "Você está se aproximando da franquia",
            "description": f"{utilization:.0f}% da franquia mensal já foi utilizada.",
            "action": "Ver meu uso",
            "tone": "warning",
            "icon": "speedometer2",
        }
    if low_energy:
        return {
            "type": "energy",
            "title": "Seu nível de combustível merece atenção",
            "description": f"Nível atual estimado: {float(telemetry.get('fuel_level_pct', 0) or 0):.0f}%.",
            "action": "Ver autonomia",
            "tone": "warning",
            "icon": "fuel-pump",
        }
    if renewal:
        return {
            "type": "contract",
            "title": "Sua renovação está se aproximando",
            "description": f"Restam aproximadamente {int(float(contract.get('months_remaining', 0) or 0))} meses no contrato.",
            "action": "Revisar contrato",
            "tone": "info",
            "icon": "file-earmark-text",
        }
    if long_trip:
        return {
            "type": "trip",
            "title": "Há um padrão de viagem na sua rotina",
            "description": "Podemos conferir KM, manutenção e condições do carro antes da próxima saída.",
            "action": "Preparar viagem",
            "tone": "info",
            "icon": "signpost-split",
        }
    if benefit:
        return {
            "type": "benefit",
            "title": "Encontramos algo útil para sua rotina",
            "description": "Existe um benefício contextual disponível para este cliente.",
            "action": "Ver benefício",
            "tone": "success",
            "icon": "gift",
        }
    return {
        "type": "neutral",
        "title": "Tudo certo por aqui",
        "description": "Nenhum sinal prioritário foi identificado pelos dados disponíveis.",
        "action": "Ver resumo",
        "tone": "success",
        "icon": "check2-circle",
    }


def _routine_patterns(trips: pd.DataFrame) -> list[dict[str, Any]]:
    if trips.empty:
        return []

    x = trips.copy()
    x["trip_date"] = pd.to_datetime(x["trip_date"], errors="coerce")
    x["hour"] = pd.to_datetime(
        x["start_time"], errors="coerce", format="%H:%M:%S"
    ).dt.hour

    patterns: list[dict[str, Any]] = []
    grouped = (
        x.groupby(["purpose", "day_of_week"])
        .agg(
            count=("trip_id", "count"),
            avg_distance=("distance_km", "mean"),
            last_trip=("trip_date", "max"),
        )
        .reset_index()
        .sort_values(["count", "last_trip"], ascending=[False, False])
        .head(3)
    )
    for row in grouped.to_dict(orient="records"):
        day = DAY_PT.get(str(row["day_of_week"]), str(row["day_of_week"]).lower())
        patterns.append(
            {
                "label": f"{day} · {row['purpose']}",
                "detail": f"{int(row['count'])} ocorrências · ~{float(row['avg_distance']):.0f} km por viagem",
                "confidence": min(98, 55 + int(row["count"]) * 8),
            }
        )

    return patterns


def _recent_recommendations(recs: pd.DataFrame) -> list[dict[str, Any]]:
    if recs.empty:
        return []
    x = recs.copy()
    x["generated_at"] = pd.to_datetime(x["generated_at"], errors="coerce")
    return records(x.sort_values("generated_at", ascending=False).head(4))


def build_dashboard(customer_id: str) -> dict[str, Any]:
    clients = load_dataset("clients")
    contracts = load_dataset("contracts")
    vehicles = load_dataset("vehicles")
    telemetry = load_dataset("telemetry")
    trips = load_dataset("trips")
    maintenance = load_dataset("maintenance")
    contexts = load_dataset("context_events")
    recs = load_dataset("recommendations")

    client_rows = clients[clients["customer_id"].astype(str).eq(customer_id)].copy()
    if client_rows.empty:
        raise ValueError("Cliente não encontrado")

    client = client_rows.iloc[0]
    customer_contracts = contracts[
        contracts["customer_id"].astype(str).eq(customer_id)
    ].copy()
    active = customer_contracts[
        customer_contracts["status"].astype(str).str.lower().eq("active")
    ]
    contract = (
        (active.iloc[0] if not active.empty else customer_contracts.iloc[0])
        if not customer_contracts.empty
        else pd.Series(dtype=object)
    )
    vehicle_id = str(contract.get("vehicle_id", ""))

    vehicle_rows = vehicles[vehicles["vehicle_id"].astype(str).eq(vehicle_id)]
    vehicle = (
        vehicle_rows.iloc[0] if not vehicle_rows.empty else pd.Series(dtype=object)
    )

    customer_telemetry = telemetry[
        telemetry["customer_id"].astype(str).eq(customer_id)
    ].copy()
    customer_telemetry["timestamp"] = pd.to_datetime(
        customer_telemetry["timestamp"], errors="coerce"
    )
    telemetry_row = (
        customer_telemetry.sort_values("timestamp").iloc[-1]
        if not customer_telemetry.empty
        else pd.Series(dtype=object)
    )

    customer_context = contexts[
        contexts["customer_id"].astype(str).eq(customer_id)
    ].copy()
    customer_context["timestamp"] = pd.to_datetime(
        customer_context["timestamp"], errors="coerce"
    )
    context = (
        customer_context.sort_values("timestamp").iloc[-1]
        if not customer_context.empty
        else pd.Series(dtype=object)
    )

    customer_trips = trips[trips["customer_id"].astype(str).eq(customer_id)].copy()
    customer_trips["trip_date"] = pd.to_datetime(
        customer_trips["trip_date"], errors="coerce"
    )
    recent_trip = (
        customer_trips.sort_values("trip_date", ascending=False).iloc[0]
        if not customer_trips.empty
        else pd.Series(dtype=object)
    )

    customer_maintenance = maintenance[
        maintenance["customer_id"].astype(str).eq(customer_id)
    ].copy()
    customer_maintenance["event_date"] = pd.to_datetime(
        customer_maintenance["event_date"], errors="coerce"
    )
    latest_maintenance = (
        customer_maintenance.sort_values("event_date", ascending=False).iloc[0]
        if not customer_maintenance.empty
        else pd.Series(dtype=object)
    )

    customer_recs = recs[recs["customer_id"].astype(str).eq(customer_id)].copy()
    today = _choose_action(context, telemetry_row, contract)

    km_available = float(telemetry_row.get("km_available", 0) or 0)
    utilization = float(telemetry_row.get("franchise_utilization_pct", 0) or 0)
    maintenance_remaining = float(telemetry_row.get("maintenance_km_remaining", 0) or 0)
    months_remaining = float(contract.get("months_remaining", 0) or 0)

    readiness_checks = [
        {
            "label": "Franquia de KM",
            "status": "ok" if utilization < 80 else "attention",
            "detail": f"{km_available:.0f} km disponíveis",
        },
        {
            "label": "Manutenção",
            "status": "attention" if maintenance_remaining <= 1000 else "ok",
            "detail": f"{maintenance_remaining:.0f} km restantes",
        },
        {
            "label": "Contrato",
            "status": "ok" if months_remaining > 3 else "attention",
            "detail": f"{months_remaining:.0f} meses restantes",
        },
        {
            "label": "Energia",
            "status": "attention"
            if float(telemetry_row.get("fuel_level_pct", 100) or 100) <= 20
            else "ok",
            "detail": f"{float(telemetry_row.get('fuel_level_pct', 0) or 0):.0f}% combustível",
        },
    ]
    readiness_ok = sum(x["status"] == "ok" for x in readiness_checks)
    readiness_score = int(round(readiness_ok / len(readiness_checks) * 100))

    routine = _routine_patterns(customer_trips)
    recent_long = customer_trips[
        customer_trips["long_trip_flag"].fillna(False).astype(bool)
    ].sort_values("trip_date", ascending=False)
    planner_trip = (
        recent_long.iloc[0]
        if not recent_long.empty
        else (recent_trip if not recent_trip.empty else pd.Series(dtype=object))
    )

    planner = {
        "headline": "Próxima saída relevante",
        "origin": str(planner_trip.get("origin_city", client.get("city", "—"))),
        "destination": str(
            planner_trip.get("destination_city", client.get("city", "—"))
        ),
        "distance_km": float(planner_trip.get("distance_km", 0) or 0),
        "purpose": str(planner_trip.get("purpose", "rotina")),
        "date": json_safe(planner_trip.get("trip_date"))
        if not planner_trip.empty
        else None,
        "long_trip": bool(planner_trip.get("long_trip_flag", False))
        if not planner_trip.empty
        else False,
        "readiness_score": readiness_score,
        "checks": readiness_checks,
        "cta": "Preparar viagem",
    }

    assistant_cards = [
        {
            "title": "Revisão",
            "subtitle": f"{maintenance_remaining:.0f} km restantes",
            "action": "Agendar",
            "type": "maintenance",
        },
        {
            "title": "KM",
            "subtitle": f"{utilization:.0f}% da franquia",
            "action": "Ver uso",
            "type": "km",
        },
        {
            "title": "Rotina",
            "subtitle": routine[0]["label"] if routine else "Sem padrão suficiente",
            "action": "Explorar",
            "type": "routine",
        },
    ]

    return {
        "customer": _first_or_empty(client_rows),
        "contract": _first_or_empty(pd.DataFrame([contract]))
        if not contract.empty
        else {},
        "vehicle": _first_or_empty(pd.DataFrame([vehicle]))
        if not vehicle.empty
        else {},
        "telemetry": _first_or_empty(pd.DataFrame([telemetry_row]))
        if not telemetry_row.empty
        else {},
        "maintenance": _first_or_empty(pd.DataFrame([latest_maintenance]))
        if not latest_maintenance.empty
        else {},
        "context": _first_or_empty(pd.DataFrame([context]))
        if not context.empty
        else {},
        "today": today,
        "planner": planner,
        "routine": routine,
        "assistant": {
            "greeting": f"Olá, {str(client.get('profile', 'motorista')).replace('_', ' ').title()}.",
            "summary": "Analisei seu carro, contrato, histórico e sinais recentes para priorizar o que pode ser útil agora.",
            "cards": assistant_cards,
            "recent_recommendations": _recent_recommendations(customer_recs),
        },
        "meta": {
            "data_origin": "SYNTHETIC",
            "note": "Dashboard conceitual construído com dados sintéticos do protótipo.",
        },
    }


def resolve_intent(question: str, customer_id: str) -> dict[str, Any]:
    dashboard = build_dashboard(customer_id)
    normalized = question.strip().lower()
    intent = "general"
    for candidate, keywords in INTENT_RULES.items():
        if any(keyword in normalized for keyword in keywords):
            intent = candidate
            break

    if intent == "maintenance":
        action = (
            dashboard["today"]
            if dashboard["today"]["type"] == "maintenance"
            else {
                "type": "maintenance",
                "title": "Confira sua próxima revisão",
                "description": f"Restam cerca de {float(dashboard['telemetry'].get('maintenance_km_remaining', 0) or 0):.0f} km.",
                "action": "Abrir manutenção",
            }
        )
    elif intent == "km":
        action = {
            "type": "km",
            "title": "Seu uso de KM",
            "description": f"Você utilizou {float(dashboard['telemetry'].get('franchise_utilization_pct', 0) or 0):.0f}% da franquia mensal.",
            "action": "Ver meu uso",
        }
    elif intent == "trip":
        action = {
            "type": "trip",
            "title": "Vamos preparar sua mobilidade",
            "description": "Posso cruzar viagem, KM, manutenção e condição atual do carro.",
            "action": "Abrir Mobility Planner",
        }
    elif intent == "benefit":
        action = {
            "type": "benefit",
            "title": "Benefícios para sua rotina",
            "description": "Existe um sinal de benefício contextual disponível neste perfil.",
            "action": "Ver benefícios",
        }
    elif intent == "contract":
        action = {
            "type": "contract",
            "title": "Resumo da sua assinatura",
            "description": f"Restam aproximadamente {float(dashboard['contract'].get('months_remaining', 0) or 0):.0f} meses no contrato.",
            "action": "Ver contrato",
        }
    elif intent == "support":
        action = {
            "type": "support",
            "title": "Vamos resolver isso",
            "description": "O assistente pode direcionar você para o serviço correspondente.",
            "action": "Abrir suporte",
        }
    else:
        action = dashboard["today"]

    return {
        "customer_id": customer_id,
        "question": question,
        "intent": intent,
        "action": action,
        "explanation": "Classificação determinística de protótipo; IA generativa não é necessária nesta primeira camada.",
    }
