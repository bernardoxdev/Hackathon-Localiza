from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Query

from app.core.data import load_dataset, records
from app.services.appstore_analysis import (
    filter_analysis,
    paginate_analysis,
    summarize_analysis,
)

router = APIRouter(prefix="/api/appstore", tags=["App Store"])


def _analysis_df():
    return load_dataset("appstore_analysis")


@router.get("/summary")
def summary() -> dict[str, Any]:
    analysis = summarize_analysis(_analysis_df())
    snapshot_df = load_dataset("appstore_snapshot")
    snapshot = {
        str(row.metric): row.value for row in snapshot_df.itertuples(index=False)
    }
    return {"analysis": analysis, "app_snapshot": snapshot}


@router.get("")
def list_reviews(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    q: str = Query(""),
    sentiment: str | None = Query(None),
    topic: str | None = Query(None),
    urgency: str | None = Query(None),
    context_opportunity: str | None = Query(None),
) -> dict[str, Any]:
    source_df = _analysis_df()
    df = filter_analysis(
        source_df,
        q=q,
        sentiment=sentiment,
        topic=topic,
        urgency=urgency,
        context_opportunity=context_opportunity,
    ).sort_values("review_date", ascending=False, na_position="last")
    page_df, total = paginate_analysis(df, page, page_size)
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": (total + page_size - 1) // page_size,
        "filters": {
            "q": q,
            "sentiment": sentiment,
            "topic": topic,
            "urgency": urgency,
            "context_opportunity": context_opportunity,
        },
        "options": {
            "sentiments": sorted(source_df["sentiment"].dropna().unique().tolist()),
            "topics": sorted(source_df["topic"].dropna().unique().tolist()),
            "journey_moments": sorted(
                source_df["journey_moment"].dropna().unique().tolist()
            ),
            "pain_categories": sorted(
                source_df["pain_category"].dropna().unique().tolist()
            ),
            "urgencies": sorted(source_df["urgency"].dropna().unique().tolist()),
            "context_opportunities": sorted(
                source_df["context_opportunity"].dropna().unique().tolist()
            ),
        },
        "rows": records(page_df),
    }


@router.get("/insights")
def insights() -> dict[str, Any]:
    summary_data = summarize_analysis(_analysis_df())
    return {
        "topics": summary_data["topics"][:10],
        "journey_moments": summary_data["journey_moments"][:10],
        "pain_categories": summary_data["pain_categories"][:10],
        "opportunities": summary_data["opportunities"][:10],
    }


@router.get("/{review_id}")
def review_detail(review_id: str) -> dict[str, Any]:
    result = _analysis_df()[_analysis_df()["review_id"].astype(str).eq(review_id)]
    if result.empty:
        raise HTTPException(status_code=404, detail="Review App Store não encontrada")
    return records(result.head(1))[0]
