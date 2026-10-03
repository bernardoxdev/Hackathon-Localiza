from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Query

from app.core.data import load_dataset, records
from app.services.reclameaqui_analysis import (
    filter_analysis,
    paginate_analysis,
    summarize_analysis,
)

router = APIRouter(prefix="/api/reclameaqui", tags=["Reclame AQUI"])


def _analysis_df():
    return load_dataset("reclameaqui_analysis")


@router.get("/summary")
def summary() -> dict[str, Any]:
    analysis = summarize_analysis(_analysis_df())
    snapshot = load_dataset("reclameaqui_snapshot")
    metrics = {str(r.metric): r.value for r in snapshot.itertuples(index=False)}
    return {"analysis": analysis, "company_snapshot": metrics}


@router.get("")
def list_complaints(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    q: str = Query(""),
    sentiment: str | None = Query(None),
    topic: str | None = Query(None),
    urgency: str | None = Query(None),
    status: str | None = Query(None),
    context_opportunity: str | None = Query(None),
) -> dict[str, Any]:
    source_df = _analysis_df()
    df = filter_analysis(
        source_df,
        q=q,
        sentiment=sentiment,
        topic=topic,
        urgency=urgency,
        status=status,
        context_opportunity=context_opportunity,
    )
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
            "status": status,
            "context_opportunity": context_opportunity,
        },
        "options": {
            "sentiments": sorted(source_df["sentiment"].dropna().unique().tolist()),
            "topics": sorted(source_df["topic"].dropna().unique().tolist()),
            "urgencies": sorted(source_df["urgency"].dropna().unique().tolist()),
            "statuses": sorted(source_df["status"].dropna().unique().tolist()),
            "context_opportunities": sorted(
                source_df["context_opportunity"].dropna().unique().tolist()
            ),
        },
        "rows": records(page_df),
    }


@router.get("/{complaint_id}")
def complaint_detail(complaint_id: str) -> dict[str, Any]:
    df = _analysis_df()
    result = df[df["complaint_id"].astype(str).eq(complaint_id)]
    if result.empty:
        raise HTTPException(status_code=404, detail="Reclamação não encontrada")
    return records(result.head(1))[0]
