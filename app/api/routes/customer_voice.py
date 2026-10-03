from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Query

from app.core.data import load_dataset, records
from app.services.appstore_analysis import filter_analysis as filter_appstore_analysis
from app.services.appstore_analysis import (
    summarize_analysis as summarize_appstore_analysis,
)
from app.services.googleplay_reviews import paginate
from app.services.reclameaqui_analysis import filter_analysis as filter_ra_analysis
from app.services.reclameaqui_analysis import (
    summarize_analysis as summarize_ra_analysis,
)
from app.services.review_analysis import filter_analysis as filter_reviews_analysis
from app.services.review_analysis import (
    summarize_analysis as summarize_reviews_analysis,
)

router = APIRouter(prefix="/api/customer-voice", tags=["Customer Voice"])


def _googleplay() -> Any:
    return load_dataset("review_analysis")


def _reclameaqui() -> Any:
    return load_dataset("reclameaqui_analysis")


def _appstore() -> Any:
    return load_dataset("appstore_analysis")


def _merge_summary(source: str) -> dict[str, Any]:
    pieces: list[dict[str, Any]] = []
    if source in {"all", "googleplay"}:
        pieces.append(
            {"source": "googleplay", **summarize_reviews_analysis(_googleplay())}
        )
    if source in {"all", "reclameaqui"}:
        pieces.append(
            {"source": "reclameaqui", **summarize_ra_analysis(_reclameaqui())}
        )
    if source in {"all", "appstore"}:
        pieces.append(
            {"source": "appstore", **summarize_appstore_analysis(_appstore())}
        )

    total = sum(x["total"] for x in pieces)

    def merge_distributions(field: str) -> dict[str, int]:
        out: dict[str, int] = {}
        for piece in pieces:
            for key, value in piece.get(field, {}).items():
                out[key] = out.get(key, 0) + int(value)
        return dict(sorted(out.items(), key=lambda item: item[1], reverse=True))

    def merge_grouped(
        field: str, key_column: str, count_column: str
    ) -> list[dict[str, Any]]:
        aggregate: dict[str, dict[str, float]] = {}
        for piece in pieces:
            for row in piece.get(field, []):
                key = str(row.get(key_column, "geral"))
                entry = aggregate.setdefault(
                    key, {"count": 0, "negative": 0, "high": 0}
                )

                # Google Play/App Store use `review_count`; Reclame AQUI
                # uses `complaint_count`. Accept both without changing the
                # public response shape of Customer Voice.
                raw_count = row.get(count_column)
                if raw_count is None:
                    raw_count = row.get("complaint_count", 0)
                entry["count"] += int(raw_count or 0)
                entry["negative"] += int(row.get("negative_count", 0) or 0)
                entry["high"] += int(row.get("high_urgency_count", 0) or 0)

        rows = []
        for key, values in aggregate.items():
            count = int(values["count"])
            negative = int(values["negative"])
            rows.append(
                {
                    key_column: key,
                    "review_count": count,
                    "complaint_count": count,
                    "negative_count": negative,
                    "high_urgency_count": int(values["high"]),
                    "share_pct": round(count / max(total, 1) * 100, 1),
                    "negative_rate_pct": round(negative / max(count, 1) * 100, 1),
                }
            )
        return sorted(
            rows, key=lambda row: (-row["negative_count"], -row["review_count"])
        )

    return {
        "source": source,
        "total": total,
        "sources": [{"source": x["source"], "total": x["total"]} for x in pieces],
        "sentiment": merge_distributions("sentiment"),
        "voice_signal": merge_distributions("voice_signal"),
        "topics": merge_grouped("topics", "topic", "review_count"),
        "journey_moments": merge_grouped(
            "journey_moments", "journey_moment", "review_count"
        ),
        "opportunities": merge_grouped(
            "opportunities", "context_opportunity", "review_count"
        ),
        "high_urgency": sum(x.get("high_urgency", 0) for x in pieces),
        "actionable": sum(x.get("actionable", 0) for x in pieces),
    }


@router.get("/summary")
def customer_voice_summary(
    source: str = Query("all", pattern="^(all|googleplay|reclameaqui|appstore)$"),
):
    return _merge_summary(source)


@router.get("")
def customer_voice_items(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    source: str = Query("all", pattern="^(all|googleplay|reclameaqui|appstore)$"),
    q: str = Query(""),
    sentiment: str | None = Query(None),
    topic: str | None = Query(None),
    urgency: str | None = Query(None),
) -> dict[str, Any]:
    frames = []
    if source in {"all", "googleplay"}:
        df = filter_reviews_analysis(
            _googleplay(), q=q, sentiment=sentiment, topic=topic, urgency=urgency
        )
        df = df.copy()
        df["source"] = "GOOGLE_PLAY"
        df["source_id"] = df["review_id"]
        df["display_text"] = df["review_text"]
        frames.append(df)
    if source in {"all", "reclameaqui"}:
        df = filter_ra_analysis(
            _reclameaqui(), q=q, sentiment=sentiment, topic=topic, urgency=urgency
        )
        df = df.copy()
        df["source"] = "RECLAME_AQUI"
        df["source_id"] = df["complaint_id"]
        df["display_text"] = df["summary"]
        frames.append(df)
    if source in {"all", "appstore"}:
        df = filter_appstore_analysis(
            _appstore(), q=q, sentiment=sentiment, topic=topic, urgency=urgency
        )
        df = df.copy()
        df["source"] = "APP_STORE"
        df["source_id"] = df["review_id"]
        df["display_text"] = (
            df["review_title"].fillna("") + ". " + df["review_text"].fillna("")
        ).str.strip(". ")
        frames.append(df)
    if not frames:
        return {
            "total": 0,
            "page": page,
            "page_size": page_size,
            "pages": 0,
            "rows": [],
        }

    merged = __import__("pandas").concat(frames, ignore_index=True, sort=False)
    if "published_at" in merged.columns:
        merged["event_date"] = merged["published_at"]
    elif "review_date" in merged.columns:
        merged["event_date"] = merged["review_date"]
    else:
        merged["event_date"] = None
    if "review_date" in merged.columns and "published_at" in merged.columns:
        merged["event_date"] = merged["event_date"].fillna(merged["review_date"])
    merged = merged.sort_values("event_date", ascending=False, na_position="last")
    page_df, total = paginate(merged, page, page_size)
    return {
        "total": int(total),
        "page": page,
        "page_size": page_size,
        "pages": (total + page_size - 1) // page_size,
        "source": source,
        "rows": records(page_df),
    }
