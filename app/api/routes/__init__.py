from app.api.routes.analytics import router as analytics_router
from app.api.routes.context import router as context_router
from app.api.routes.customers import router as customers_router
from app.api.routes.datasets import router as datasets_router
from app.api.routes.health import router as health_router
from app.api.routes.metadata import router as metadata_router
from app.api.routes.pages import router as pages_router
from app.api.routes.review_analysis import router as review_analysis_router
from app.api.routes.reviews import router as reviews_router

__all__ = [
    "analytics_router",
    "context_router",
    "customers_router",
    "datasets_router",
    "health_router",
    "metadata_router",
    "pages_router",
    "review_analysis_router",
    "reviews_router",
]
