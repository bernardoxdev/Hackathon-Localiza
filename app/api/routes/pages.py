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


@router.get("/reclame-aqui", include_in_schema=False)
def reclame_aqui() -> FileResponse:
    return FileResponse(TEMPLATE_DIR / "dashboard" / "voice_of_customer.html")


@router.get("/localiza-app", include_in_schema=False)
def localiza_app() -> FileResponse:
    return FileResponse(TEMPLATE_DIR / "prototype" / "localiza_app.html")


@router.get("/app-store", include_in_schema=False)
def app_store() -> FileResponse:
    return FileResponse(TEMPLATE_DIR / "dashboard" / "voice_of_customer.html")


@router.get("/mobility-dashboard", include_in_schema=False)
def mobility_dashboard_page() -> FileResponse:
    return FileResponse(TEMPLATE_DIR / "prototype" / "mobility_dashboard.html")


@router.get("/mobility-planner", include_in_schema=False)
def mobility_planner_page() -> FileResponse:
    return FileResponse(TEMPLATE_DIR / "prototype" / "mobility_planner.html")


@router.get("/mobility-today", include_in_schema=False)
def mobility_today_page() -> FileResponse:
    return FileResponse(TEMPLATE_DIR / "prototype" / "mobility_today.html")


@router.get("/mobility-routine", include_in_schema=False)
def mobility_routine_page() -> FileResponse:
    return FileResponse(TEMPLATE_DIR / "prototype" / "mobility_routine.html")


@router.get("/mobility-assistant", include_in_schema=False)
def mobility_assistant_page() -> FileResponse:
    return FileResponse(TEMPLATE_DIR / "prototype" / "mobility_assistant.html")
