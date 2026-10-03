from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app
from app.services.assistant import TOOLS, _fallback_reply
from app.services.rag import customer_rag

client = TestClient(app)


def test_assistant_tools_are_registered() -> None:
    assert "get_km_status" in TOOLS
    assert "get_maintenance_status" in TOOLS
    assert "get_trip_readiness" in TOOLS


def test_assistant_fallback_returns_contextual_answer() -> None:
    result = _fallback_reply("CUST0001", "Quanto ainda posso rodar?")
    assert result["engine"] == "fallback-rag"
    assert result["intent"] == "km"
    assert "franquia" in result["message"].lower()


def test_assistant_message_endpoint_without_api_key() -> None:
    response = client.post(
        "/api/assistant/message",
        json={
            "customer_id": "CUST0001",
            "message": "Quanto ainda posso rodar?",
            "history": [],
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["intent"] == "km"
    assert payload["data_origin"] == "SYNTHETIC"


def test_assistant_capabilities_endpoint() -> None:
    response = client.get("/api/assistant/capabilities")
    assert response.status_code == 200
    payload = response.json()
    names = {tool["name"] for tool in payload["tools"]}
    assert "get_km_status" in names
    assert "get_contextual_benefits" in names


def test_rag_filters_context_by_customer_and_vehicle() -> None:
    result = customer_rag.retrieve(
        "CUST0001", "Quanto ainda posso rodar com meu carro?", top_k=8
    )
    assert result.customer_id == "CUST0001"
    assert result.vehicle_id == "VEH0001"
    assert result.vehicle_type == "Sedan"
    assert result.documents
    assert result.documents[0].metadata["customer_id"] == "CUST0001"
    assert any(document.source == "vehicle_profile" for document in result.documents)
    assert all(
        document.metadata.get("vehicle_id") == "VEH0001"
        for document in result.documents
    )


def test_rag_rejects_unknown_customer() -> None:
    try:
        customer_rag.retrieve("CUST9999", "Quero saber sobre meu carro")
    except ValueError as exc:
        assert "Cliente não encontrado" in str(exc)
    else:
        raise AssertionError("RAG deveria rejeitar cliente inexistente")
