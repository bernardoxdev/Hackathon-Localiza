from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.assistant import TOOLS, assistant_service
from app.services.rag import customer_rag

router = APIRouter(prefix="/api/assistant", tags=["Assistant"])


class ChatMessage(BaseModel):
    role: str
    content: str = Field(min_length=1, max_length=4000)


class AssistantRequest(BaseModel):
    customer_id: str = Field(default="CUST0001", min_length=1)
    message: str = Field(min_length=1, max_length=4000)
    history: list[ChatMessage] = Field(default_factory=list, max_length=20)


class AssistantResponse(BaseModel):
    message: str
    engine: str
    model: str | None = None
    intent: str
    tool_calls: list[str] = Field(default_factory=list)
    action: dict[str, Any] | None = None
    data_origin: str
    notice: str | None = None
    rag: dict[str, Any] | None = None


@router.post("/message", response_model=AssistantResponse)
async def assistant_message(payload: AssistantRequest) -> AssistantResponse:
    try:
        result = await assistant_service.reply(
            customer_id=payload.customer_id,
            message=payload.message,
            history=[item.model_dump() for item in payload.history],
        )
        return AssistantResponse(**result)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover - runtime/provider errors
        raise HTTPException(
            status_code=502,
            detail=f"Falha ao processar o assistente: {exc}",
        ) from exc


@router.get("/capabilities")
def assistant_capabilities() -> dict[str, Any]:
    return {
        "llm_enabled": assistant_service.llm_enabled,
        "model": assistant_service.model if assistant_service.llm_enabled else None,
        "tools": [
            {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.parameters,
            }
            for tool in TOOLS.values()
        ],
    }


@router.get("/retrieval")
def assistant_retrieval(
    customer_id: str = "CUST0001",
    q: str = "resumo do meu carro",
) -> dict[str, Any]:
    """Expõe o RAG para depuração e demonstração do contexto recuperado."""
    return customer_rag.retrieve(customer_id, q).as_dict()
