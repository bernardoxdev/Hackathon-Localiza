from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_appstore_summary():
    response = client.get("/api/appstore/summary")
    assert response.status_code == 200
    data = response.json()
    assert data["analysis"]["total"] == 4
    assert data["app_snapshot"]["app_id"] == "1528537131"
    assert data["app_snapshot"]["rating"] == "4.8"


def test_appstore_rows():
    response = client.get("/api/appstore?page=1&page_size=4")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == len(data["rows"])
    assert len(data["rows"]) == 4
    assert all(row["source"] == "APP_STORE" for row in data["rows"])


def test_customer_voice_appstore_filter():
    response = client.get("/api/customer-voice?source=appstore&page_size=20")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == len(data["rows"])
    assert all(row["source"] == "APP_STORE" for row in data["rows"])


def test_appstore_page():
    response = client.get("/app-store?source=appstore")
    assert response.status_code == 200
    assert "App Store" in response.text
