from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.routes import (
    analytics_router,
    appstore_router,
    assistant_router,
    context_router,
    customer_voice_router,
    customers_router,
    datasets_router,
    health_router,
    metadata_router,
    mobility_router,
    pages_router,
    reclameaqui_router,
    review_analysis_router,
    reviews_router,
)

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(
    title="RUPTURA 2026 — Case 2 Mobility Data Explorer",
    description="Dashboard conceitual para explorar dados, voz do cliente e experiências contextuais do protótipo Localiza Assinatura.",
    version="1.5.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

for router in (
    pages_router,
    customer_voice_router,
    health_router,
    datasets_router,
    analytics_router,
    assistant_router,
    appstore_router,
    customers_router,
    context_router,
    metadata_router,
    mobility_router,
    reclameaqui_router,
    review_analysis_router,
    reviews_router,
):
    app.include_router(router)
