from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Query

from app.services.googleplay_reviews import filter_reviews, paginate, summarize_reviews

router = APIRouter(prefix="/api/reviews", tags=["Google Play Reviews"])


from app.core.data import load_dataset, records


def _dataframe_from_main(name: str):
    return load_dataset(name)


def _review_records(df) -> list[dict[str, Any]]:
    return records(df)


@router.get("")
def list_reviews(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    q: str = Query(""),
    rating: int | None = Query(None, ge=1, le=5),
    app_version: str | None = Query(None),
    has_reply: bool | None = Query(None),
) -> dict[str, Any]:
    df = filter_reviews(
        _dataframe_from_main("googleplay_reviews"),
        q=q,
        rating=rating,
        app_version=app_version,
        has_reply=has_reply,
    )
    page_df, total = paginate(df, page, page_size)

    versions = sorted(
        x for x in df["app_version"].dropna().astype(str).unique().tolist() if x
    )

    return {
        "total": int(total),
        "page": page,
        "page_size": page_size,
        "pages": (total + page_size - 1) // page_size,
        "filters": {
            "q": q,
            "rating": rating,
            "app_version": app_version,
            "has_reply": has_reply,
        },
        "available_versions": versions,
        "rows": _review_records(page_df),
    }


@router.get("/summary")
def reviews_summary() -> dict[str, Any]:
    return summarize_reviews(_dataframe_from_main("googleplay_reviews"))


@router.get("/{review_id}")
def review_detail(review_id: str) -> dict[str, Any]:
    df = _dataframe_from_main("googleplay_reviews")
    result = df[df["review_id"].astype(str).eq(review_id)]
    if result.empty:
        raise HTTPException(status_code=404, detail="Review não encontrada")
    return _review_records(result.head(1))[0]
