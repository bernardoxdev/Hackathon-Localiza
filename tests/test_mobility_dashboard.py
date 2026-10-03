from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_mobility_dashboard_page():
    response = client.get("/mobility-dashboard")
    assert response.status_code == 200
    assert "Mobility Companion" in response.text
    assert "Mobility Planner" in response.text
    assert "O QUE EU PRECISO HOJE?" in response.text


def test_mobility_dashboard_api():
    response = client.get("/api/mobility-dashboard", params={"customer_id": "CUST0001"})
    assert response.status_code == 200
    data = response.json()
    assert data["customer"]["customer_id"] == "CUST0001"
    assert "planner" in data
    assert "routine" in data
    assert "assistant" in data
    assert "today" in data


def test_mobility_intent_api():
    response = client.get(
        "/api/mobility-dashboard/intent",
        params={"customer_id": "CUST0001", "q": "Preciso fazer minha revisão"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["intent"] == "maintenance"
    assert data["action"]["action"] == "Agendar revisão"
