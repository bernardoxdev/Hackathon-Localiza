from __future__ import annotations

from typing import Any

import pandas as pd


ANALYSIS_COLUMNS = [
    "review_id",
    "rating",
    "review_text",
    "review_date",
    "app_version",
    "thumbs_up_count",
    "reply_content",
    "data_origin",
    "normalized_text",
    "sentiment",
    "sentiment_score",
    "sentiment_confidence",
    "voice_signal",
    "topic",
    "journey_moment",
    "pain_category",
    "urgency",
    "product_area",
    "context_opportunity",
    "recommended_action",
    "confidence",
    "matched_signals",
    "analysis_method",
]


def _safe_mean(series: pd.Series) -> float:
    values = pd.to_numeric(series, errors="coerce").dropna()
    return round(float(values.mean()), 2) if not values.empty else 0.0


def summarize_analysis(df: pd.DataFrame) -> dict[str, Any]:
    if df.empty:
        return {
            "total": 0,
            "sentiment": {},
            "topics": [],
            "journey_moments": [],
            "pain_categories": [],
            "opportunities": [],
            "high_urgency": 0,
            "actionable": 0,
        }

    total = len(df)

    def distribution(column: str) -> dict[str, int]:
        return {
            str(k): int(v)
            for k, v in df[column].fillna("nao_classificado").value_counts().items()
        }

    def grouped(column: str) -> list[dict[str, Any]]:
        grouped_df = (
            df.groupby(column, dropna=False)
            .agg(
                review_count=("review_id", "count"),
                average_rating=("rating", _safe_mean),
                negative_count=("sentiment", lambda s: int((s == "negativo").sum())),
                high_urgency_count=("urgency", lambda s: int((s == "alta").sum())),
            )
            .reset_index()
        )
        grouped_df["share_pct"] = (
            grouped_df["review_count"].div(max(total, 1)).mul(100).round(1)
        )
        grouped_df["negative_rate_pct"] = (
            grouped_df["negative_count"]
            .div(grouped_df["review_count"].clip(lower=1))
            .mul(100)
            .round(1)
        )
        grouped_df = grouped_df.sort_values(
            ["negative_count", "review_count"], ascending=[False, False]
        )
        result = []
        for row in grouped_df.to_dict(orient="records"):
            cleaned = {}
            for key, value in row.items():
                if pd.isna(value):
                    cleaned[str(key)] = None
                elif isinstance(value, (int, bool)):
                    cleaned[str(key)] = int(value)
                elif isinstance(value, float):
                    cleaned[str(key)] = float(value)
                else:
                    cleaned[str(key)] = value
            result.append(cleaned)
        return result

    actionable_mask = df["recommended_action"].fillna("nenhuma").ne("nenhuma")

    return {
        "total": int(total),
        "sentiment": distribution("sentiment"),
        "voice_signal": distribution("voice_signal"),
        "topics": grouped("topic"),
        "journey_moments": grouped("journey_moment"),
        "pain_categories": grouped("pain_category"),
        "opportunities": grouped("context_opportunity"),
        "high_urgency": int(df["urgency"].eq("alta").sum()),
        "actionable": int(actionable_mask.sum()),
        "actionable_rate_pct": round(float(actionable_mask.mean() * 100), 1),
    }


def filter_analysis(
    df: pd.DataFrame,
    *,
    q: str = "",
    sentiment: str | None = None,
    topic: str | None = None,
    journey_moment: str | None = None,
    pain_category: str | None = None,
    urgency: str | None = None,
    context_opportunity: str | None = None,
) -> pd.DataFrame:
    result = df.copy()
    if q.strip():
        query = q.strip().lower()
        mask = result["review_text"].fillna("").astype(str).str.lower().str.contains(
            query, na=False
        )
        result = result.loc[mask]

    for column, value in [
        ("sentiment", sentiment),
        ("topic", topic),
        ("journey_moment", journey_moment),
        ("pain_category", pain_category),
        ("urgency", urgency),
        ("context_opportunity", context_opportunity),
    ]:
        if value:
            result = result.loc[result[column].fillna("").eq(value)]

    return result


def paginate_analysis(
    df: pd.DataFrame, page: int, page_size: int
) -> tuple[pd.DataFrame, int]:
    total = len(df)
    start = (page - 1) * page_size
    return df.iloc[start : start + page_size], total
