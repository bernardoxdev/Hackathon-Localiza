from __future__ import annotations

from typing import Any

import pandas as pd


REVIEW_COLUMNS = [
    "review_id",
    "author_name",
    "rating",
    "review_text",
    "thumbs_up_count",
    "app_version",
    "review_date",
    "reply_content",
    "reply_date",
    "app_id",
    "language",
    "country",
    "source",
    "data_origin",
]


def filter_reviews(
    df: pd.DataFrame,
    *,
    q: str = "",
    rating: int | None = None,
    app_version: str | None = None,
    has_reply: bool | None = None,
) -> pd.DataFrame:
    result = df.copy()

    if q.strip():
        query = q.strip().lower()
        mask = result["review_text"].fillna("").astype(str).str.lower().str.contains(
            query, na=False
        )
        result = result.loc[mask]

    if rating is not None:
        result = result.loc[pd.to_numeric(result["rating"], errors="coerce").eq(rating)]

    if app_version:
        result = result.loc[result["app_version"].fillna("").eq(app_version)]

    if has_reply is not None:
        replied = result["reply_content"].fillna("").astype(str).str.strip().ne("")
        result = result.loc[replied.eq(has_reply)]

    return result


def paginate(df: pd.DataFrame, page: int, page_size: int) -> tuple[pd.DataFrame, int]:
    total = len(df)
    start = (page - 1) * page_size
    return df.iloc[start : start + page_size], total


def summarize_reviews(df: pd.DataFrame) -> dict[str, Any]:
    if df.empty:
        return {
            "total": 0,
            "average_rating": 0.0,
            "rating_distribution": {},
            "rating_percentages": {},
            "replied_count": 0,
            "reply_rate": 0.0,
            "date_range": {"min": None, "max": None},
            "app_versions": {},
            "top_reviews": [],
        }

    ratings = pd.to_numeric(df["rating"], errors="coerce").dropna()
    reply_mask = df["reply_content"].fillna("").astype(str).str.strip().ne("")
    dates = pd.to_datetime(df["review_date"], errors="coerce").dropna()

    distribution = ratings.astype(int).value_counts().sort_index().to_dict()
    percentages = (
        ratings.astype(int)
        .value_counts(normalize=True)
        .sort_index()
        .mul(100)
        .round(1)
        .to_dict()
    )

    top = (
        df.assign(_thumbs=pd.to_numeric(df["thumbs_up_count"], errors="coerce").fillna(0))
        .sort_values(["_thumbs", "review_date"], ascending=[False, False])
        .head(10)
    )

    top_reviews = []
    for _, row in top.iterrows():
        top_reviews.append(
            {
                "review_id": row.get("review_id"),
                "rating": int(row["rating"]) if pd.notna(row.get("rating")) else None,
                "review_text": row.get("review_text"),
                "thumbs_up_count": int(row["_thumbs"]),
                "review_date": row.get("review_date"),
                "app_version": row.get("app_version"),
            }
        )

    return {
        "total": int(len(df)),
        "average_rating": round(float(ratings.mean()), 2) if not ratings.empty else 0.0,
        "rating_distribution": {str(k): int(v) for k, v in distribution.items()},
        "rating_percentages": {str(k): float(v) for k, v in percentages.items()},
        "replied_count": int(reply_mask.sum()),
        "reply_rate": round(float(reply_mask.mean() * 100), 1),
        "date_range": {
            "min": dates.min().isoformat() if not dates.empty else None,
            "max": dates.max().isoformat() if not dates.empty else None,
        },
        "app_versions": {
            str(k): int(v)
            for k, v in df["app_version"].fillna("Sem versão").value_counts().head(10).items()
        },
        "top_reviews": top_reviews,
    }
