from __future__ import annotations

import json
import os
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from app.services.mobility_dashboard import build_dashboard, resolve_intent
from app.services.rag import RAGResult, customer_rag

try:
    from openai import AsyncOpenAI
except ImportError:  # pragma: no cover - keeps the fallback usable before sync
    AsyncOpenAI = None  # type: ignore[assignment,misc]

from pathlib import Path

PROMPTS_DIR = Path(__file__).resolve().parents[1] / "prompts"
ASSISTANT_PROMPT_PATH = PROMPTS_DIR / "assistant_contextual.md"

# ============================================================================
# CONFIGURAÇÃO DO ASSISTENTE
# ============================================================================
# Edite principalmente esta seção quando quiser mudar o comportamento do
# chatbot sem mexer na camada de integração com o modelo.
RESPONSE_BEHAVIOR = {
    "language": "pt-BR",
    "tone": "natural, próximo e objetivo",
    "max_sentences": 5,
    "use_bullets_when_useful": True,
    "never_invent_customer_data": True,
    "never_invent_actions": True,
    "mention_synthetic_data_when_relevant": True,
}

AI_PROVIDER = os.getenv("AI_PROVIDER", "ollama").strip().lower()
ASSISTANT_MODEL = os.getenv("LOCALIZA_ASSISTANT_MODEL", "qwen2.5:3b-instruct-q4_K_M")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434/v1")

if AI_PROVIDER == "openai":
    _LLM_API_KEY = OPENAI_API_KEY
    _LLM_BASE_URL = None
elif AI_PROVIDER == "ollama":
    _LLM_API_KEY = os.getenv("OLLAMA_API_KEY", "ollama")
    _LLM_BASE_URL = OLLAMA_BASE_URL
else:
    _LLM_API_KEY = None
    _LLM_BASE_URL = None


@dataclass(frozen=True, slots=True)
class ToolDefinition:
    name: str
    description: str
    parameters: dict[str, Any]
    function: Callable[..., dict[str, Any]]


TOOLS: dict[str, ToolDefinition] = {}


def register_tool(
    name: str,
    description: str,
    parameters: dict[str, Any] | None = None,
):
    """Registra uma função Python que pode ser chamada pelo LLM.

    Para adicionar uma nova capacidade ao assistente, crie uma função normal
    e use este decorator. O modelo passa a enxergar automaticamente a função.

    Exemplo:

    @register_tool(
        "get_benefits",
        "Consulta benefícios contextuais disponíveis para o cliente.",
    )
    def get_benefits(customer_id: str) -> dict[str, Any]:
        return {...}
    """

    def decorator(function: Callable[..., dict[str, Any]]):
        TOOLS[name] = ToolDefinition(
            name=name,
            description=description,
            parameters=parameters
            or {
                "type": "object",
                "properties": {},
                "required": [],
                "additionalProperties": False,
            },
            function=function,
        )
        return function

    return decorator


# ============================================================================
# FUNÇÕES DE NEGÓCIO / TOOLS
# ============================================================================
# Estas são as funções que você vai expandir com regras reais da Localiza.
# O LLM apenas decide quando chamar cada uma e transforma o resultado em
# linguagem natural. Cálculos e regras ficam aqui no Python.


@register_tool(
    "get_customer_context",
    "Consulta o contexto principal do cliente, contrato, carro e cidade.",
)
def get_customer_context(customer_id: str) -> dict[str, Any]:
    dashboard = build_dashboard(customer_id)
    customer = dashboard.get("customer", {})
    contract = dashboard.get("contract", {})
    vehicle = dashboard.get("vehicle", {})
    telemetry = dashboard.get("telemetry", {})

    return {
        "customer_id": customer_id,
        "profile": customer.get("profile"),
        "city": customer.get("city"),
        "state": customer.get("state"),
        "preferred_channel": customer.get("preferred_channel"),
        "consent_location": customer.get("consent_location"),
        "consent_personalization": customer.get("consent_personalization"),
        "vehicle": {
            "make": vehicle.get("make"),
            "model": vehicle.get("model"),
            "version": vehicle.get("version"),
            "year": vehicle.get("year"),
        },
        "contract": {
            "contract_id": contract.get("contract_id"),
            "status": contract.get("status"),
            "months_remaining": contract.get("months_remaining"),
            "monthly_km_allowance": contract.get("monthly_km_allowance"),
            "renewal_date": contract.get("renewal_date"),
        },
        "telemetry": {
            "vehicle_status": telemetry.get("vehicle_status"),
            "city_region": telemetry.get("city_region"),
        },
        "data_origin": "SYNTHETIC",
    }


@register_tool(
    "get_km_status",
    "Consulta uso mensal de KM, franquia e KM disponível.",
)
def get_km_status(customer_id: str) -> dict[str, Any]:
    dashboard = build_dashboard(customer_id)
    telemetry = dashboard.get("telemetry", {})

    used = float(telemetry.get("km_used_month", 0) or 0)
    allowance = float(telemetry.get("monthly_km_allowance", 0) or 0)
    available = float(telemetry.get("km_available", 0) or 0)
    utilization = float(telemetry.get("franchise_utilization_pct", 0) or 0)

    return {
        "km_used_month": round(used, 1),
        "monthly_km_allowance": round(allowance, 1),
        "km_available": round(available, 1),
        "utilization_pct": round(utilization, 1),
        "status": "attention" if utilization >= 80 else "ok",
        "action": {
            "type": "km",
            "title": "Seu uso de KM",
            "description": f"Você utilizou {utilization:.0f}% da franquia mensal e tem cerca de {available:.0f} km disponíveis.",
            "label": "Ver meu uso",
        },
        "data_origin": "SYNTHETIC",
    }


@register_tool(
    "get_maintenance_status",
    "Consulta a próxima manutenção e os sinais de manutenção do veículo.",
)
def get_maintenance_status(customer_id: str) -> dict[str, Any]:
    dashboard = build_dashboard(customer_id)
    telemetry = dashboard.get("telemetry", {})
    maintenance = dashboard.get("maintenance", {})

    remaining = float(
        telemetry.get("maintenance_km_remaining", maintenance.get("km_remaining", 0))
        or 0
    )

    return {
        "km_remaining": round(remaining, 1),
        "maintenance_type": maintenance.get("maintenance_type"),
        "maintenance_class": maintenance.get("maintenance_class"),
        "status": maintenance.get("status"),
        "workshop": maintenance.get("workshop_name"),
        "estimated_cost_brl": maintenance.get("estimated_cost_brl"),
        "duration_hours": maintenance.get("duration_hours"),
        "tire_status": maintenance.get("tire_status"),
        "oil_status": maintenance.get("oil_status"),
        "battery_status": maintenance.get("battery_status"),
        "brake_status": maintenance.get("brake_status"),
        "action": {
            "type": "maintenance",
            "title": "Sua próxima manutenção",
            "description": f"Restam cerca de {remaining:.0f} km para a próxima manutenção registrada no protótipo.",
            "label": "Agendar revisão",
        },
        "data_origin": "SYNTHETIC",
    }


@register_tool(
    "get_contract_status",
    "Consulta status, prazo restante e renovação do contrato.",
)
def get_contract_status(customer_id: str) -> dict[str, Any]:
    dashboard = build_dashboard(customer_id)
    contract = dashboard.get("contract", {})
    months_remaining = float(contract.get("months_remaining", 0) or 0)

    return {
        "contract_id": contract.get("contract_id"),
        "status": contract.get("status"),
        "months_remaining": round(months_remaining, 1),
        "renewal_date": contract.get("renewal_date"),
        "auto_renew_preference": contract.get("auto_renew_preference"),
        "monthly_km_allowance": contract.get("monthly_km_allowance"),
        "monthly_fee_brl": contract.get("monthly_fee_brl"),
        "action": {
            "type": "contract",
            "title": "Resumo da sua assinatura",
            "description": f"O contrato do protótipo possui aproximadamente {months_remaining:.0f} meses restantes.",
            "label": "Ver contrato",
        },
        "data_origin": "SYNTHETIC",
    }


@register_tool(
    "get_trip_readiness",
    "Avalia uma viagem usando KM disponível, manutenção e uma distância informada ou a viagem longa mais recente.",
    parameters={
        "type": "object",
        "properties": {
            "distance_km": {
                "anyOf": [{"type": "number"}, {"type": "null"}],
                "description": "Distância estimada da viagem em km. Use null quando o cliente ainda não informou.",
            }
        },
        "required": ["distance_km"],
        "additionalProperties": False,
    },
)
def get_trip_readiness(
    customer_id: str,
    distance_km: float | None = None,
) -> dict[str, Any]:
    dashboard = build_dashboard(customer_id)
    planner = dashboard.get("planner", {})
    telemetry = dashboard.get("telemetry", {})

    available = float(telemetry.get("km_available", 0) or 0)
    maintenance_remaining = float(telemetry.get("maintenance_km_remaining", 0) or 0)
    reference_distance = (
        float(distance_km)
        if distance_km is not None
        else float(planner.get("distance_km", 0) or 0)
    )

    km_ok = reference_distance <= available if reference_distance > 0 else None
    maintenance_ok = (
        reference_distance <= maintenance_remaining
        if reference_distance > 0 and maintenance_remaining > 0
        else None
    )

    checks = {
        "km": {
            "available": round(available, 1),
            "trip_distance": round(reference_distance, 1),
            "ok": km_ok,
        },
        "maintenance": {
            "remaining": round(maintenance_remaining, 1),
            "trip_distance": round(reference_distance, 1),
            "ok": maintenance_ok,
        },
    }

    if reference_distance <= 0:
        status = "needs_more_information"
    elif km_ok is False or maintenance_ok is False:
        status = "attention"
    else:
        status = "ready"

    return {
        "status": status,
        "checks": checks,
        "recent_trip": {
            "origin": planner.get("origin"),
            "destination": planner.get("destination"),
            "purpose": planner.get("purpose"),
        },
        "action": {
            "type": "trip",
            "title": "Preparar sua viagem",
            "description": "Posso cruzar a distância da viagem com seu KM disponível e a próxima manutenção.",
            "label": "Abrir Mobility Planner",
        },
        "data_origin": "SYNTHETIC",
    }


@register_tool(
    "get_customer_routine",
    "Consulta os principais padrões de rotina identificados no histórico de viagens.",
)
def get_customer_routine(customer_id: str) -> dict[str, Any]:
    dashboard = build_dashboard(customer_id)
    routine = dashboard.get("routine", [])
    return {
        "patterns": routine,
        "has_enough_history": bool(routine),
        "data_origin": "SYNTHETIC",
    }


@register_tool(
    "get_contextual_benefits",
    "Consulta sinais e recomendações de benefícios contextuais do cliente.",
)
def get_contextual_benefits(customer_id: str) -> dict[str, Any]:
    dashboard = build_dashboard(customer_id)
    context = dashboard.get("context", {})
    recommendations = dashboard.get("assistant", {}).get("recent_recommendations", [])

    benefit_recommendations = [
        row
        for row in recommendations
        if str(row.get("recommendation_type", "")).lower() == "benefit"
    ]

    available = bool(context.get("benefit_available")) or bool(benefit_recommendations)
    return {
        "available": available,
        "signal": context.get("benefit_available"),
        "recommendations": benefit_recommendations[:3],
        "action": {
            "type": "benefit",
            "title": "Benefícios para sua rotina",
            "description": "Há um sinal de benefício contextual no protótipo para este cliente."
            if available
            else "Não há benefício contextual identificado neste momento.",
            "label": "Ver benefícios",
        },
        "data_origin": "SYNTHETIC",
    }


@register_tool(
    "get_recent_recommendations",
    "Consulta as recomendações contextuais mais recentes geradas para o cliente.",
)
def get_recent_recommendations(customer_id: str) -> dict[str, Any]:
    dashboard = build_dashboard(customer_id)
    return {
        "recommendations": dashboard.get("assistant", {}).get(
            "recent_recommendations", []
        ),
        "data_origin": "SYNTHETIC",
    }


# ============================================================================
# ASSISTENTE
# ============================================================================
def _load_prompt_template() -> str:
    if not ASSISTANT_PROMPT_PATH.exists():
        raise FileNotFoundError(f"Prompt não encontrado: {ASSISTANT_PROMPT_PATH}")

    return ASSISTANT_PROMPT_PATH.read_text(encoding="utf-8")


def _build_instructions(rag_result: RAGResult) -> str:
    behavior = RESPONSE_BEHAVIOR

    template = _load_prompt_template()

    replacements = {
        "{{LANGUAGE}}": behavior["language"],
        "{{TONE}}": behavior["tone"],
        "{{MAX_SENTENCES}}": str(behavior["max_sentences"]),
        "{{CUSTOMER_ID}}": rag_result.customer_id,
        "{{VEHICLE_ID}}": rag_result.vehicle_id,
        "{{VEHICLE_TYPE}}": rag_result.vehicle_type,
        "{{RAG_CONTEXT}}": rag_result.context_text,
    }

    for placeholder, value in replacements.items():
        template = template.replace(
            placeholder,
            str(value),
        )

    return template.strip()


def _tool_schemas() -> list[dict[str, Any]]:
    return [
        {
            "type": "function",
            "function": {
                "name": definition.name,
                "description": definition.description,
                "parameters": definition.parameters,
            },
        }
        for definition in TOOLS.values()
    ]


def _extract_action(tool_results: list[dict[str, Any]]) -> dict[str, Any] | None:
    priority = {
        "maintenance": 1,
        "km": 2,
        "trip": 3,
        "contract": 4,
        "benefit": 5,
        "routine": 6,
    }
    candidates = [
        result.get("action") for result in tool_results if result.get("action")
    ]
    if not candidates:
        return None
    return sorted(
        candidates,
        key=lambda item: priority.get(str(item.get("type")), 99),
    )[0]


def _intent_from_tools(tool_names: list[str]) -> str:
    mapping = {
        "get_maintenance_status": "maintenance",
        "get_km_status": "km",
        "get_trip_readiness": "trip",
        "get_contract_status": "contract",
        "get_contextual_benefits": "benefit",
        "get_customer_routine": "routine",
    }
    for name in tool_names:
        if name in mapping:
            return mapping[name]
    return "general"


def _history_to_messages(
    history: list[dict[str, str]], message: str
) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for entry in history[-20:]:
        role = str(entry.get("role", "")).strip().lower()
        content = str(entry.get("content", "")).strip()
        if role not in {"user", "assistant"} or not content:
            continue
        items.append({"role": role, "content": content})
    items.append({"role": "user", "content": message})
    return items


def _fallback_reply(
    customer_id: str,
    message: str,
    rag_result: RAGResult | None = None,
) -> dict[str, Any]:
    """Fallback local que continua consultando o RAG antes de responder."""
    rag_result = rag_result or customer_rag.retrieve(customer_id, message)
    result = resolve_intent(message, customer_id)
    action = result.get("action", {})
    intent = result.get("intent", "general")

    summary = rag_result.documents[0].text if rag_result.documents else ""
    responses = {
        "maintenance": f"{action.get('title', 'Manutenção')}. {action.get('description', '')}",
        "km": f"{action.get('title', 'Uso de KM')}. {action.get('description', '')}",
        "trip": "Posso verificar sua viagem cruzando KM disponível e manutenção. Me diga aproximadamente quantos quilômetros você pretende rodar.",
        "benefit": f"{action.get('title', 'Benefícios')}. {action.get('description', '')}",
        "contract": f"{action.get('title', 'Contrato')}. {action.get('description', '')}",
        "support": f"{action.get('title', 'Suporte')}. {action.get('description', '')}",
        "general": "Consultei seus dados e posso falar sobre seu carro, KM, manutenção, contrato, benefícios e rotina. O que você precisa resolver agora?",
    }

    normalized_action = dict(action or {})
    if "label" not in normalized_action and normalized_action.get("action"):
        normalized_action["label"] = normalized_action["action"]

    return {
        "message": responses.get(intent, responses["general"]),
        "engine": "fallback-rag",
        "model": None,
        "intent": intent,
        "tool_calls": [],
        "action": normalized_action or None,
        "data_origin": "SYNTHETIC",
        "rag": rag_result.as_dict(),
        "notice": "Configure o Ollama e baixe o modelo local para ativar a conversa com IA.",
        "_rag_summary": summary,
    }


class AssistantService:
    """Orquestra RAG, LLM, ferramentas Python e fallback local."""

    def __init__(self) -> None:
        self.model = ASSISTANT_MODEL
        self.provider = AI_PROVIDER
        self.client = (
            AsyncOpenAI(api_key=_LLM_API_KEY, base_url=_LLM_BASE_URL)
            if AsyncOpenAI and _LLM_API_KEY
            else None
        )

    @property
    def llm_enabled(self) -> bool:
        return self.client is not None

    async def reply(
        self,
        customer_id: str,
        message: str,
        history: list[dict[str, str]] | None = None,
    ) -> dict[str, Any]:
        history = history or []

        # REGRA: toda solicitação passa pelo RAG antes de qualquer resposta.
        rag_result = customer_rag.retrieve(customer_id, message)

        if not self.client:
            return _fallback_reply(customer_id, message, rag_result)

        messages = [
            {
                "role": "system",
                "content": _build_instructions(rag_result),
            },
            *_history_to_messages(history, message),
        ]
        tool_results: list[dict[str, Any]] = []
        called_tools: list[str] = []
        response = None

        # Limita o número de rodadas de tool-calling para manter previsibilidade.
        for _ in range(4):
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=_tool_schemas(),
                tool_choice="auto",
                max_tokens=500,
            )

            assistant_message = response.choices[0].message
            assistant_payload: dict[str, Any] = {
                "role": "assistant",
                "content": assistant_message.content or "",
            }
            if assistant_message.tool_calls:
                assistant_payload["tool_calls"] = [
                    {
                        "id": call.id,
                        "type": "function",
                        "function": {
                            "name": call.function.name,
                            "arguments": call.function.arguments,
                        },
                    }
                    for call in assistant_message.tool_calls
                ]
            messages.append(assistant_payload)

            tool_calls = assistant_message.tool_calls or []
            if not tool_calls:
                break

            for call in tool_calls:
                definition = TOOLS.get(call.function.name)
                if not definition:
                    result = {"error": f"Tool desconhecida: {call.function.name}"}
                else:
                    try:
                        arguments = json.loads(call.function.arguments or "{}")
                        result = definition.function(
                            customer_id=customer_id,
                            **arguments,
                        )
                        result = customize_tool_result(
                            call.function.name,
                            result,
                            customer_id,
                        )
                    except Exception as exc:  # pragma: no cover - defensive path
                        result = {
                            "error": "Não foi possível consultar esta funcionalidade.",
                            "details": str(exc),
                        }

                called_tools.append(call.function.name)
                tool_results.append(result)
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": call.id,
                        "content": json.dumps(result, ensure_ascii=False, default=str),
                    }
                )

        final_message = ""
        if response is not None:
            final_message = (response.choices[0].message.content or "").strip()
        if not final_message:
            return _fallback_reply(customer_id, message, rag_result)

        return {
            "message": final_message,
            "engine": self.provider,
            "model": self.model,
            "intent": _intent_from_tools(called_tools),
            "tool_calls": called_tools,
            "action": _extract_action(tool_results),
            "data_origin": "SYNTHETIC",
            "rag": rag_result.as_dict(),
        }


assistant_service = AssistantService()


# ============================================================================
# PONTO DE EXTENSÃO PARA NOVAS RESPOSTAS
# ============================================================================
# Você pode alterar esta função para criar mensagens/ações específicas antes
# de enviar os resultados ao LLM. Exemplo: bloquear agendamento fora de horário,
# pedir confirmação, exigir origem/destino etc.
def customize_tool_result(
    tool_name: str,
    result: dict[str, Any],
    customer_id: str,
) -> dict[str, Any]:
    """Hook de negócio para personalizar resultados das ferramentas."""
    return result


# ============================================================================
# PONTO DE EXTENSÃO PARA NOVAS RESPOSTAS
# ============================================================================
# Você pode alterar esta função para criar mensagens/ações específicas antes
# de enviar os resultados ao LLM. Exemplo: bloquear agendamento fora de horário,
# pedir confirmação, exigir origem/destino etc.
def customize_tool_result(
    tool_name: str,
    result: dict[str, Any],
    customer_id: str,
) -> dict[str, Any]:
    """Hook de negócio para personalizar resultados das ferramentas."""
    return result
