from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Query

from app.core.data import load_dataset, records
from app.services.review_analysis import (
    filter_analysis,
    paginate_analysis,
    summarize_analysis,
)

router = APIRouter(prefix="/api/reviews", tags=["Review Analysis"])


def _analysis_df():
    return load_dataset("review_analysis")


@router.get("/analysis-summary")
def analysis_summary() -> dict[str, Any]:
    return summarize_analysis(_analysis_df())


@router.get("/analysis")
def list_analysis(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    q: str = Query(""),
    sentiment: str | None = Query(None),
    topic: str | None = Query(None),
    journey_moment: str | None = Query(None),
    pain_category: str | None = Query(None),
    urgency: str | None = Query(None),
    context_opportunity: str | None = Query(None),
) -> dict[str, Any]:
    source_df = _analysis_df()
    df = filter_analysis(
        source_df,
        q=q,
        sentiment=sentiment,
        topic=topic,
        journey_moment=journey_moment,
        pain_category=pain_category,
        urgency=urgency,
        context_opportunity=context_opportunity,
    )
    page_df, total = paginate_analysis(df, page, page_size)

    return {
        "total": int(total),
        "page": page,
        "page_size": page_size,
        "pages": (total + page_size - 1) // page_size,
        "filters": {
            "q": q,
            "sentiment": sentiment,
            "topic": topic,
            "journey_moment": journey_moment,
            "pain_category": pain_category,
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
def analysis_insights() -> dict[str, Any]:
    summary = summarize_analysis(_analysis_df())
    return {
        "topics": summary["topics"][:10],
        "journey_moments": summary["journey_moments"][:10],
        "pain_categories": summary["pain_categories"][:10],
        "opportunities": summary["opportunities"][:10],
    }
