from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Query

from app.services.mobility_dashboard import build_dashboard, resolve_intent

router = APIRouter(prefix="/api/mobility-dashboard", tags=["Mobility Companion"])


@router.get("")
def mobility_dashboard(
    customer_id: str = Query("CUST0001", min_length=1),
) -> dict[str, Any]:
    try:
        return build_dashboard(customer_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/intent")
def mobility_intent(
    customer_id: str = Query("CUST0001", min_length=1),
    q: str = Query("", min_length=1),
) -> dict[str, Any]:
    try:
        return resolve_intent(q, customer_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
