from __future__ import annotations

import json
import logging
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import pandas as pd

from app.core.data import DATA_DIR

logger = logging.getLogger(__name__)

APP_ID = "1528537131"
DEFAULT_COUNTRY = "br"
DEFAULT_PAGES = 10
MAX_PUBLIC_RSS_PAGES = 10
REVIEWS_PER_RSS_PAGE = 50
OUTPUT_PATH = DATA_DIR / "appstore" / "app_store_reviews.csv"
SNAPSHOT_PATH = DATA_DIR / "appstore" / "appstore_snapshot.csv"
SOURCE_URL = "https://apps.apple.com/br/app/localiza-assinatura-meoo/id1528537131"
RSS_TEMPLATE = (
    "https://itunes.apple.com/{country}/rss/customerreviews/page={page}/"
    "id={app_id}/sortby=mostrecent/json"
)

REVIEW_COLUMNS = [
    "review_id",
    "author_name",
    "rating",
    "review_title",
    "review_text",
    "review_date",
    "app_version",
    "app_id",
    "country",
    "language",
    "source",
    "source_url",
    "data_origin",
    "collection_method",
    "is_preview",
]


def _label(entry: dict, key: str) -> str | None:
    value = entry.get(key)
    if isinstance(value, dict):
        return value.get("label")
    return value


def fetch_page(
    page: int, *, country: str = DEFAULT_COUNTRY, app_id: str = APP_ID
) -> list[dict]:
    url = RSS_TEMPLATE.format(country=country, page=page, app_id=app_id)
    request = Request(url, headers={"User-Agent": "Mozilla/5.0 Hackathon-Localiza"})
    try:
        with urlopen(request, timeout=20) as response:
            payload = json.load(response)
    except (HTTPError, URLError, TimeoutError) as exc:
        raise RuntimeError(f"Falha ao consultar Apple App Store RSS: {url}") from exc

    entries = payload.get("feed", {}).get("entry", []) or []
    if isinstance(entries, dict):
        entries = [entries]
    return entries


def normalize_entries(
    entries: list[dict], *, country: str, app_id: str
) -> pd.DataFrame:
    rows: list[dict] = []
    for entry in entries:
        rating = _label(entry, "im:rating")
        if rating is None:
            continue
        author = entry.get("author", {})
        link = entry.get("link", {})
        if isinstance(link, list):
            link = link[0] if link else {}
        link_attrs = link.get("attributes", {}) if isinstance(link, dict) else {}
        rows.append(
            {
                "review_id": _label(entry, "id"),
                "author_name": _label(author, "name")
                if isinstance(author, dict)
                else None,
                "rating": int(rating) if rating is not None else None,
                "review_title": _label(entry, "title"),
                "review_text": _label(entry, "content"),
                "review_date": _label(entry, "updated"),
                "app_version": _label(entry, "im:version"),
                "app_id": app_id,
                "country": country.upper(),
                "language": "pt-BR",
                "source": "APP_STORE",
                "source_url": link_attrs.get("href") or SOURCE_URL,
                "data_origin": "APPLE_APP_STORE",
                "collection_method": "APPLE_RSS_PUBLIC_FEED",
                "is_preview": False,
            }
        )
    return pd.DataFrame(rows, columns=REVIEW_COLUMNS)


def collect_reviews(
    *, country: str = DEFAULT_COUNTRY, app_id: str = APP_ID, pages: int = DEFAULT_PAGES
) -> pd.DataFrame:
    requested_pages = min(max(int(pages), 1), MAX_PUBLIC_RSS_PAGES)
    if pages > MAX_PUBLIC_RSS_PAGES:
        logger.warning(
            "Apple App Store RSS é limitado a %s páginas públicas; usando o máximo.",
            MAX_PUBLIC_RSS_PAGES,
        )

    entries: list[dict] = []
    seen: set[str] = set()
    for page in range(1, requested_pages + 1):
        page_entries = fetch_page(page, country=country, app_id=app_id)
        if not page_entries:
            break
        new_entries = 0
        for entry in page_entries:
            review_id = _label(entry, "id")
            if review_id and review_id not in seen:
                seen.add(review_id)
                entries.append(entry)
                new_entries += 1
        logger.info(
            "Apple App Store | página %s/%s | novos registros: %s | acumuladas: %s",
            page,
            requested_pages,
            new_entries,
            len(entries),
        )
        if new_entries == 0:
            break

    logger.info(
        "Apple App Store | coleta concluída | reviews acumuladas: %s | limite teórico do feed: ~%s",
        len(entries),
        requested_pages * REVIEWS_PER_RSS_PAGE,
    )
    return normalize_entries(entries, country=country, app_id=app_id)


def create_reviews(
    *, country: str = DEFAULT_COUNTRY, app_id: str = APP_ID, pages: int = DEFAULT_PAGES
) -> Path:
    df = collect_reviews(country=country, app_id=app_id, pages=pages)
    if df.empty:
        raise RuntimeError("Nenhuma review do App Store foi coletada.")
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.sort_values("review_date", ascending=False).drop_duplicates("review_id").to_csv(
        OUTPUT_PATH, index=False
    )
    return OUTPUT_PATH


def create_preview_dataset() -> Path:
    """Create a tiny public-page preview when live RSS is unavailable.

    The excerpts are intentionally short. They are not a substitute for the live
    Apple feed and are marked with is_preview=True.
    """
    rows = [
        {
            "review_id": "appstore-preview-001",
            "author_name": "keylacristhi",
            "rating": None,
            "review_title": "Muito pratico",
            "review_text": "Prático, rápido, descomplicado!",
            "review_date": "2023-02-28",
            "app_version": None,
            "app_id": APP_ID,
            "country": "BR",
            "language": "pt-BR",
            "source": "APP_STORE",
            "source_url": SOURCE_URL,
            "data_origin": "APPLE_APP_STORE",
            "collection_method": "PUBLIC_PAGE_PREVIEW",
            "is_preview": True,
        },
        {
            "review_id": "appstore-preview-002",
            "author_name": "Tati P Oliveira",
            "rating": None,
            "review_title": "Bom, mas pode melhorar",
            "review_text": "As informações precisam estar completas",
            "review_date": "2026-09-03",
            "app_version": "4.20.0",
            "app_id": APP_ID,
            "country": "BR",
            "language": "pt-BR",
            "source": "APP_STORE",
            "source_url": SOURCE_URL,
            "data_origin": "APPLE_APP_STORE",
            "collection_method": "PUBLIC_PAGE_PREVIEW",
            "is_preview": True,
        },
        {
            "review_id": "appstore-preview-003",
            "author_name": "JamilsonVeras",
            "rating": None,
            "review_title": "Muito bom",
            "review_text": "Muito bom",
            "review_date": "2026-07-03",
            "app_version": "4.14.1",
            "app_id": APP_ID,
            "country": "BR",
            "language": "pt-BR",
            "source": "APP_STORE",
            "source_url": SOURCE_URL,
            "data_origin": "APPLE_APP_STORE",
            "collection_method": "PUBLIC_PAGE_PREVIEW",
            "is_preview": True,
        },
        {
            "review_id": "appstore-preview-004",
            "author_name": "Selva, Brasil!",
            "rating": None,
            "review_title": "PC",
            "review_text": "Está sendo muito importante a utilização",
            "review_date": "2026-07-12",
            "app_version": "4.16.0",
            "app_id": APP_ID,
            "country": "BR",
            "language": "pt-BR",
            "source": "APP_STORE",
            "source_url": SOURCE_URL,
            "data_origin": "APPLE_APP_STORE",
            "collection_method": "PUBLIC_PAGE_PREVIEW",
            "is_preview": True,
        },
    ]
    df = pd.DataFrame(rows, columns=REVIEW_COLUMNS)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)
    return OUTPUT_PATH


def write_snapshot() -> Path:
    rows = [
        {"metric": "app_id", "value": APP_ID},
        {"metric": "app_name", "value": "Localiza Assinatura (Meoo)"},
        {"metric": "rating", "value": "4.8"},
        {"metric": "rating_count", "value": "6300"},
        {"metric": "latest_version", "value": "5.0.0"},
        {"metric": "size_mb", "value": "164.9"},
        {"metric": "min_ios", "value": "15.0"},
        {"metric": "category", "value": "Entretenimento"},
        {"metric": "country", "value": "BR"},
        {"metric": "source", "value": "APPLE_APP_STORE_PAGE"},
        {"metric": "source_url", "value": SOURCE_URL},
        {"metric": "collected_on", "value": "2026-10-02"},
        {"metric": "collection_method", "value": "PUBLIC_APP_STORE_PAGE"},
    ]
    SNAPSHOT_PATH.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(SNAPSHOT_PATH, index=False)
    return SNAPSHOT_PATH
