from pathlib import Path

from fastapi.testclient import TestClient

from app.ingest import reclameaqui as reclameaqui_ingest
from app.main import app

client = TestClient(app)


def test_reclameaqui_summary():
    response = client.get("/api/reclameaqui/summary")
    assert response.status_code == 200
    data = response.json()
    assert data["analysis"]["total"] >= 1
    assert int(data["company_snapshot"]["reclamacoes_ativas_listadas"]) == 12659


def test_reclameaqui_rows():
    response = client.get("/api/reclameaqui?page=1&page_size=5")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= len(data["rows"])
    assert len(data["rows"]) == 5
    assert all(row["source"] == "RECLAME_AQUI" for row in data["rows"])


def test_customer_voice_combined():
    response = client.get("/api/customer-voice/summary?source=all")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == sum(item["total"] for item in data["sources"])
    assert {row["source"] for row in data["sources"]} == {
        "googleplay",
        "reclameaqui",
        "appstore",
    }


def test_customer_voice_reclameaqui_filter():
    response = client.get("/api/customer-voice?source=reclameaqui&page_size=100")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= len(data["rows"])
    assert all(row["source"] == "RECLAME_AQUI" for row in data["rows"])


def test_reclameaqui_detail():
    first = client.get("/api/reclameaqui?page=1&page_size=1").json()["rows"][0]
    response = client.get(f"/api/reclameaqui/{first['complaint_id']}")
    assert response.status_code == 200
    assert response.json()["complaint_id"] == first["complaint_id"]


def test_reclameaqui_page():
    response = client.get("/reclame-aqui?source=reclameaqui")
    assert response.status_code == 200
    assert "Reclame AQUI" in response.text


def test_reclameaqui_collector_uses_safe_default_delay():
    assert reclameaqui_ingest.DEFAULT_DELAY_SECONDS >= 1.0
    assert reclameaqui_ingest.DEFAULT_403_ATTEMPTS >= 4


def test_reclameaqui_progress_paths_are_defined():
    assert reclameaqui_ingest.PROGRESS_PATH.name == "reclameaqui_progress.csv"
    assert reclameaqui_ingest.PROGRESS_META_PATH.name == "reclameaqui_progress.json"


def test_customer_voice_reclameaqui_summary_has_grouped_counts():
    response = client.get("/api/customer-voice/summary?source=reclameaqui")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 15
    assert data["topics"]
    assert sum(item["review_count"] for item in data["topics"]) == data["total"]
    assert sum(item["complaint_count"] for item in data["topics"]) == data["total"]
    assert all(0 <= item["share_pct"] <= 100 for item in data["topics"])
    assert all(0 <= item["negative_rate_pct"] <= 100 for item in data["topics"])
    assert data["opportunities"]


def test_reclameaqui_page_defaults_to_reclameaqui_source():
    # The same template serves the consolidated page, but the path itself
    # must select the Reclame AQUI dataset by default.
    source_js = (Path("app/static/voice.js")).read_text()
    assert "window.location.pathname === '/reclame-aqui'" in source_js
