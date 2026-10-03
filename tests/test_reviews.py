from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_reviews_route_returns_rows():
    response = client.get("/api/reviews?page=1&page_size=5")
    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] == 754
    assert len(payload["rows"]) == 5
    assert "review_text" in payload["rows"][0]


def test_reviews_summary():
    response = client.get("/api/reviews/summary")
    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] == 754
    assert 1 <= payload["average_rating"] <= 5
    assert set(payload["rating_distribution"]) == {"1", "2", "3", "4", "5"}


def test_reviews_filter_by_rating():
    response = client.get("/api/reviews?rating=1&page_size=200")
    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] == 197
    assert all(row["rating"] == 1 for row in payload["rows"])


def test_reviews_search_text():
    response = client.get("/api/reviews?q=aplicativo&page_size=100")
    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] > 0
    assert all(
        "aplicativo" in (row["review_text"] or "").lower() for row in payload["rows"]
    )


def test_review_detail():
    first = client.get("/api/reviews?page=1&page_size=1").json()["rows"][0]
    response = client.get(f"/api/reviews/{first['review_id']}")
    assert response.status_code == 200
    assert response.json()["review_id"] == first["review_id"]
