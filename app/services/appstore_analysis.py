from __future__ import annotations

from typing import Any

import pandas as pd

from app.ingest.review_pipeline import (
    JOURNEY_MAP,
    OPPORTUNITY_MAP,
    PRODUCT_AREA_MAP,
    TOPIC_RULES,
    build_insights,
    classify_by_rules,
    classify_pain,
    classify_sentiment,
    classify_urgency,
    classify_voice_signal,
    normalize_text,
)

ANALYSIS_COLUMNS = [
    "review_id",
    "author_name",
    "rating",
    "review_title",
    "review_text",
    "review_date",
    "app_version",
    "app_id",
    "country",
    "language",
    "source",
    "source_url",
    "data_origin",
    "collection_method",
    "is_preview",
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

PIPELINE_VERSION = "appstore-rule-engine-v1"


def analyze_reviews(df: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for row in df.to_dict(orient="records"):
        text = " ".join(
            str(value)
            for value in [row.get("review_title", ""), row.get("review_text", "")]
            if value and not pd.isna(value)
        )
        sentiment, score, sentiment_confidence, sentiment_evidence = classify_sentiment(
            text, row.get("rating")
        )
        topic, topic_evidence = classify_by_rules(text, TOPIC_RULES)
        if topic == "geral" and sentiment == "negativo":
            topic = "funcionalidade_usabilidade"
            topic_evidence = ["fallback:sentimento_negativo"]

        pain, pain_evidence = classify_pain(text, topic, sentiment)
        urgency = classify_urgency(text, row.get("rating"), sentiment, pain)
        voice_signal = classify_voice_signal(text, sentiment)
        opportunity, action = OPPORTUNITY_MAP.get(topic, ("none", "nenhuma"))
        if sentiment != "negativo" and topic == "geral":
            opportunity, action = "none", "nenhuma"

        product_area = PRODUCT_AREA_MAP.get(topic, "experiencia_app")
        journey = JOURNEY_MAP.get(topic, "uso_do_app")
        evidence = sentiment_evidence + topic_evidence + pain_evidence
        confidence = max(0.5, min(0.98, sentiment_confidence))
        if topic != "geral":
            confidence = min(0.98, confidence + 0.08)
        if pain not in {"nenhuma", "geral"}:
            confidence = min(0.98, confidence + 0.04)

        rows.append(
            {
                **row,
                "source": "APP_STORE",
                "data_origin": row.get("data_origin", "APPLE_APP_STORE"),
                "normalized_text": normalize_text(text),
                "sentiment": sentiment,
                "sentiment_score": score,
                "sentiment_confidence": sentiment_confidence,
                "voice_signal": voice_signal,
                "topic": topic,
                "journey_moment": journey,
                "pain_category": pain,
                "urgency": urgency,
                "product_area": product_area,
                "context_opportunity": opportunity,
                "recommended_action": action,
                "confidence": round(confidence, 2),
                "matched_signals": " | ".join(dict.fromkeys(evidence)),
                "analysis_method": PIPELINE_VERSION,
            }
        )

    result = pd.DataFrame(rows)
    for column in ANALYSIS_COLUMNS:
        if column not in result.columns:
            result[column] = None
    return result[ANALYSIS_COLUMNS]


def summarize_analysis(df: pd.DataFrame) -> dict[str, Any]:
    if df.empty:
        return {
            "total": 0,
            "average_rating": None,
            "sentiment": {},
            "voice_signal": {},
            "topics": [],
            "journey_moments": [],
            "pain_categories": [],
            "opportunities": [],
            "high_urgency": 0,
            "actionable": 0,
            "actionable_rate_pct": 0.0,
            "preview_count": 0,
            "live_count": 0,
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
        return grouped_df.sort_values(
            ["negative_count", "review_count"], ascending=[False, False]
        ).to_dict(orient="records")

    ratings = pd.to_numeric(df["rating"], errors="coerce").dropna()
    actionable = df["recommended_action"].fillna("nenhuma").ne("nenhuma")
    preview = df["is_preview"].fillna(False).astype(bool)
    return {
        "total": int(total),
        "average_rating": round(float(ratings.mean()), 2)
        if not ratings.empty
        else None,
        "sentiment": distribution("sentiment"),
        "voice_signal": distribution("voice_signal"),
        "topics": grouped("topic"),
        "journey_moments": grouped("journey_moment"),
        "pain_categories": grouped("pain_category"),
        "opportunities": grouped("context_opportunity"),
        "high_urgency": int(df["urgency"].eq("alta").sum()),
        "actionable": int(actionable.sum()),
        "actionable_rate_pct": round(float(actionable.mean() * 100), 1),
        "preview_count": int(preview.sum()),
        "live_count": int((~preview).sum()),
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
        mask = result["review_title"].fillna("").astype(str).str.lower().str.contains(
            query, na=False
        ) | result["review_text"].fillna("").astype(str).str.lower().str.contains(
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


def build_appstore_insights(df: pd.DataFrame) -> pd.DataFrame:
    return build_insights(df)
