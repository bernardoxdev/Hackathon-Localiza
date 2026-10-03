from __future__ import annotations

from typing import Any

import pandas as pd

from app.ingest.review_pipeline import (
    JOURNEY_MAP,
    OPPORTUNITY_MAP,
    PRODUCT_AREA_MAP,
    TOPIC_RULES,
    classify_by_rules,
    classify_pain,
    classify_sentiment,
    classify_urgency,
    classify_voice_signal,
    normalize_text,
)

ANALYSIS_COLUMNS = [
    "complaint_id",
    "title",
    "summary",
    "published_at",
    "status",
    "city",
    "state",
    "source_url",
    "data_origin",
    "source",
    "collection_method",
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


def analyze_complaints(df: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for row in df.to_dict(orient="records"):
        combined = f"{row.get('title', '')}. {row.get('summary', '')}"
        normalized = normalize_text(combined)
        sentiment, score, sentiment_confidence, sentiment_evidence = classify_sentiment(
            combined, 1
        )
        topic, topic_evidence = classify_by_rules(combined, TOPIC_RULES)
        pain, pain_evidence = classify_pain(combined, topic, sentiment)
        urgency = classify_urgency(combined, 1, sentiment, pain)
        voice_signal = classify_voice_signal(combined, sentiment)
        opportunity, action = OPPORTUNITY_MAP.get(
            topic, ("none", "Nenhuma ação classificada")
        )
        if sentiment == "positivo" and topic == "geral":
            opportunity, action = "none", "Nenhuma ação classificada"
        product_area = PRODUCT_AREA_MAP.get(topic, "experiencia_app")
        journey = JOURNEY_MAP.get(topic, "uso_do_app")
        evidence = sentiment_evidence + topic_evidence + pain_evidence
        if row.get("status"):
            evidence.append(f"status:{normalize_text(row['status'])}")
        if row.get("city"):
            evidence.append(f"city:{normalize_text(row['city'])}")
        confidence = round(
            min(0.97, sentiment_confidence + (0.04 if topic != "geral" else 0)), 2
        )
        rows.append(
            {
                **row,
                "data_origin": row.get("data_origin", "EXTERNAL_PUBLIC"),
                "source": "RECLAME_AQUI",
                "collection_method": row.get(
                    "collection_method", "PUBLIC_WEB_SNAPSHOT"
                ),
                "normalized_text": normalized,
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
                "confidence": confidence,
                "matched_signals": " | ".join(dict.fromkeys(evidence)),
                "analysis_method": "reclameaqui-rule-engine-v1",
            }
        )

    result = pd.DataFrame(rows)
    for column in ANALYSIS_COLUMNS:
        if column not in result.columns:
            result[column] = ""
    return result[ANALYSIS_COLUMNS]


def summarize_analysis(df: pd.DataFrame) -> dict[str, Any]:
    if df.empty:
        return {
            "total": 0,
            "sentiment": {},
            "voice_signal": {},
            "topics": [],
            "journey_moments": [],
            "pain_categories": [],
            "opportunities": [],
            "high_urgency": 0,
            "actionable": 0,
            "resolved": 0,
            "responded": 0,
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
                complaint_count=("complaint_id", "count"),
                negative_count=("sentiment", lambda s: int((s == "negativo").sum())),
                high_urgency_count=("urgency", lambda s: int((s == "alta").sum())),
            )
            .reset_index()
        )
        grouped_df["share_pct"] = (
            grouped_df["complaint_count"].div(max(total, 1)).mul(100).round(1)
        )
        grouped_df["negative_rate_pct"] = (
            grouped_df["negative_count"]
            .div(grouped_df["complaint_count"].clip(lower=1))
            .mul(100)
            .round(1)
        )
        grouped_df = grouped_df.sort_values(
            ["negative_count", "complaint_count"], ascending=[False, False]
        )
        return grouped_df.to_dict(orient="records")

    actionable = (
        df["recommended_action"]
        .fillna("Nenhuma ação classificada")
        .ne("Nenhuma ação classificada")
    )
    status_norm = df["status"].fillna("").astype(str).str.lower()
    resolved = status_norm.str.contains("resolv", na=False)
    responded = status_norm.str.contains("respond", na=False) | resolved

    return {
        "total": int(total),
        "sentiment": distribution("sentiment"),
        "voice_signal": distribution("voice_signal"),
        "topics": grouped("topic"),
        "journey_moments": grouped("journey_moment"),
        "pain_categories": grouped("pain_category"),
        "opportunities": grouped("context_opportunity"),
        "high_urgency": int(df["urgency"].eq("alta").sum()),
        "actionable": int(actionable.sum()),
        "actionable_rate_pct": round(float(actionable.mean() * 100), 1),
        "resolved": int(resolved.sum()),
        "resolved_rate_pct": round(float(resolved.mean() * 100), 1),
        "responded": int(responded.sum()),
        "responded_rate_pct": round(float(responded.mean() * 100), 1),
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
    status: str | None = None,
) -> pd.DataFrame:
    result = df.copy()
    if q.strip():
        query = q.strip().lower()
        mask = result["summary"].fillna("").astype(str).str.lower().str.contains(
            query, na=False
        ) | result["title"].fillna("").astype(str).str.lower().str.contains(
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
        ("status", status),
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
