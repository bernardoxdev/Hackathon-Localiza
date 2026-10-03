from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_mobility_experience_pages_are_available():
    paths = [
        "/mobility-dashboard",
        "/mobility-planner",
        "/mobility-today",
        "/mobility-routine",
        "/mobility-assistant",
    ]
    for path in paths:
        response = client.get(path)
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]


def test_mobility_dashboard_api_supports_current_customer():
    response = client.get("/api/mobility-dashboard?customer_id=CUST0001")
    assert response.status_code == 200
    payload = response.json()
    assert "planner" in payload
    assert "routine" in payload
    assert "assistant" in payload
    assert "today" in payload


def test_mobility_intent_api_resolves_maintenance():
    response = client.get(
        "/api/mobility-dashboard/intent",
        params={"customer_id": "CUST0001", "q": "Preciso fazer minha revisão"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["intent"] == "maintenance"
    assert "action" in payload
