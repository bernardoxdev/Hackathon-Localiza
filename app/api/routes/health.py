from __future__ import annotations

from typing import Any

from fastapi import APIRouter

from app.core.data import DATASETS

router = APIRouter(prefix="/api", tags=["Health"])


@router.get("/health")
def health() -> dict[str, Any]:
    return {"status": "ok", "datasets": len(DATASETS)}
