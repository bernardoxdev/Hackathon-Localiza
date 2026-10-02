from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import FileResponse

BASE_DIR = Path(__file__).resolve().parents[3]
TEMPLATE_DIR = BASE_DIR / "app" / "templates"

router = APIRouter(tags=["Pages"])


@router.get("/", include_in_schema=False)
def index() -> FileResponse:
    return FileResponse(TEMPLATE_DIR / "dashboard" / "index.html")


@router.get("/prototype", include_in_schema=False)
def prototype() -> FileResponse:
    return FileResponse(TEMPLATE_DIR / "prototype" / "index.html")


@router.get("/voice-of-customer", include_in_schema=False)
def voice_of_customer() -> FileResponse:
    return FileResponse(TEMPLATE_DIR / "dashboard" / "voice_of_customer.html")


@router.get("/localiza-app", include_in_schema=False)
def localiza_app() -> FileResponse:
    return FileResponse(TEMPLATE_DIR / "prototype" / "localiza_app.html")
