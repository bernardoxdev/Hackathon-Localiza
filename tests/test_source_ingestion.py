from __future__ import annotations

from app.ingest import appstore_reviews, reclameaqui


def test_appstore_collector_uses_all_public_rss_pages(monkeypatch):
    calls: list[int] = []

    def fake_fetch(page: int, *, country: str, app_id: str):
        calls.append(page)
        if page > 3:
            return []
        return [
            {
                "id": {"label": f"review-{page}"},
                "author": {"name": {"label": f"user-{page}"}},
                "im:rating": {"label": "5"},
                "title": {"label": "Ótimo"},
                "content": {"label": "Muito bom"},
                "updated": {"label": f"2026-10-0{page}T00:00:00-03:00"},
                "im:version": {"label": "5.0.0"},
                "link": {
                    "attributes": {
                        "href": "https://apps.apple.com/br/app/localiza-assinatura-meoo/id1528537131"
                    }
                },
            }
        ]

    monkeypatch.setattr(appstore_reviews, "fetch_page", fake_fetch)
    df = appstore_reviews.collect_reviews(pages=10)

    assert calls == [1, 2, 3, 4]
    assert len(df) == 3
    assert set(df["review_id"]) == {"review-1", "review-2", "review-3"}


def test_reclameaqui_normalizes_public_bff_payload():
    payload = {
        "complaints": [
            {
                "id": "abc",
                "title": "Problema",
                "description": "Descrição",
                "solved": False,
                "city": "Belo Horizonte",
                "state": "MG",
                "status": "PENDING",
                "created": "2026-10-02T12:00:00-03:00",
                "company": {
                    "id": "123",
                    "name": "Localiza Meoo",
                    "shortname": "localiza-meoo",
                },
            }
        ],
        "categories": [],
        "products": [],
        "problems": [],
    }

    df = reclameaqui.normalize_complaints(payload)

    assert len(df) == 1
    assert df.iloc[0]["complaint_id"] == "abc"
    assert df.iloc[0]["company_id"] == "123"
    assert df.iloc[0]["collection_method"] == "RECLAME_AQUI_PUBLIC_BFF"


def test_reclameaqui_collector_paginates_until_empty(monkeypatch):
    calls: list[int] = []

    payloads = {
        0: {
            "complaints": [
                {"id": str(i), "title": f"A{i}", "created": "2026-10-02"}
                for i in range(10)
            ]
        },
        1: {
            "complaints": [
                {"id": str(10 + i), "title": f"B{i}", "created": "2026-10-01"}
                for i in range(10)
            ]
        },
        2: {"complaints": []},
    }

    def fake_fetch(page: int, *, company_id: str, per_page: int):
        calls.append(page)
        return payloads[page]

    monkeypatch.setattr(reclameaqui, "fetch_complaints_page", fake_fetch)
    df, metadata = reclameaqui.collect_all_complaints(
        company_id="123", per_page=10, delay_seconds=0
    )

    assert calls == [0, 1, 2]
    assert len(df) == 20
    assert metadata["complaints_collected"] == 20
    assert metadata["pages_fetched"] == 3
