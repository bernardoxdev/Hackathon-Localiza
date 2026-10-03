
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_voice_of_customer_page():
    response = client.get("/voice-of-customer")
    assert response.status_code == 200
    assert "Voz do Cliente" in response.text


def test_voice_analysis_endpoints():
    summary = client.get("/api/reviews/analysis-summary")
    assert summary.status_code == 200
    body = summary.json()
    assert body["total"] == 754
    assert body["high_urgency"] > 0

    rows = client.get("/api/reviews/analysis?page=1&page_size=5&urgency=alta")
    assert rows.status_code == 200
    data = rows.json()
    assert data["rows"]
    assert all(row["urgency"] == "alta" for row in data["rows"])
