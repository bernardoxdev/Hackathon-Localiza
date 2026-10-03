from __future__ import annotations

import csv
import json
import logging
import random
import time
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import pandas as pd

from app.core.data import DATA_DIR

logger = logging.getLogger(__name__)

SOURCE_URL = "https://www.reclameaqui.com.br/empresa/localiza-meoo/lista-reclamacoes/"
BFF_BASE_URL = "https://morpheus-bff.reclameaqui.com.br"
COMPANY_SEARCH_PATH = "/v1/companies"
COMPLAINTS_PATH = "/v1/complaints"
COMPANY_SLUG = "localiza-meoo"
COMPANY_NAME = "Localiza Meoo"
DEFAULT_PER_PAGE = 10
DEFAULT_DELAY_SECONDS = 1.2
DEFAULT_TIMEOUT = 30
DEFAULT_403_ATTEMPTS = 6
DEFAULT_403_BACKOFF_SECONDS = 10.0
OUTPUT_PATH = DATA_DIR / "reclameaqui" / "reclameaqui_complaints.csv"
SNAPSHOT_PATH = DATA_DIR / "reclameaqui" / "reclameaqui_snapshot.csv"
PROGRESS_PATH = DATA_DIR / "reclameaqui" / "reclameaqui_progress.csv"
PROGRESS_META_PATH = DATA_DIR / "reclameaqui" / "reclameaqui_progress.json"

REVIEW_COLUMNS = [
    "complaint_id",
    "title",
    "summary",
    "status",
    "solved",
    "city",
    "state",
    "published_at",
    "source_url",
    "company_id",
    "company_name",
    "company_shortname",
    "data_origin",
    "collection_method",
]


class ReclameAquiCollectionError(RuntimeError):
    """Raised when public Reclame AQUI collection cannot be completed."""


def _request_json(
    url: str,
    *,
    timeout: int = DEFAULT_TIMEOUT,
    attempts: int = 4,
    forbidden_attempts: int = DEFAULT_403_ATTEMPTS,
    forbidden_backoff_seconds: float = DEFAULT_403_BACKOFF_SECONDS,
) -> Any:
    last_error: Exception | None = None
    forbidden_retries = 0

    for attempt in range(1, attempts + 1):
        request = Request(
            url,
            headers={
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
                "Referer": SOURCE_URL,
                "Origin": "https://www.reclameaqui.com.br",
                "User-Agent": (
                    "Mozilla/5.0 (X11; Linux x86_64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/140.0.0.0 Safari/537.36"
                ),
            },
        )
        try:
            with urlopen(request, timeout=timeout) as response:  # nosec B310
                return json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            last_error = exc

            if exc.code == 403:
                forbidden_retries += 1
                if forbidden_retries >= forbidden_attempts:
                    break

                retry_after = exc.headers.get("Retry-After") if exc.headers else None
                try:
                    wait_seconds = float(retry_after) if retry_after else 0.0
                except (TypeError, ValueError):
                    wait_seconds = 0.0

                if wait_seconds <= 0:
                    wait_seconds = min(
                        forbidden_backoff_seconds * (2 ** (forbidden_retries - 1)),
                        120.0,
                    )

                wait_seconds += random.uniform(0.5, 1.5)
                logger.warning(
                    "Reclame AQUI | HTTP 403 | tentativa de recuperação %s/%s | aguardando %.1fs | url=%s",
                    forbidden_retries,
                    forbidden_attempts - 1,
                    wait_seconds,
                    url,
                )
                time.sleep(wait_seconds)
                continue

            if exc.code not in {429, 500, 502, 503, 504}:
                break
        except (URLError, TimeoutError, OSError, json.JSONDecodeError) as exc:
            last_error = exc

        if attempt < attempts:
            time.sleep(min(2.0 * attempt, 6.0))

    raise ReclameAquiCollectionError(
        f"Falha ao consultar Reclame AQUI: {url}. Erro: {last_error}"
    ) from last_error


def _extract_list(payload: Any, *keys: str) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    if not isinstance(payload, dict):
        return []

    for key in keys:
        value = payload.get(key)
        if isinstance(value, list):
            return [item for item in value if isinstance(item, dict)]

    for value in payload.values():
        if isinstance(value, dict):
            nested = _extract_list(value, *keys)
            if nested:
                return nested
    return []


def resolve_company_id() -> str:
    """Resolve the current public BFF company identifier from the slug/name."""
    params = urlencode({"text": COMPANY_NAME, "page": 0, "size": 50})
    payload = _request_json(f"{BFF_BASE_URL}{COMPANY_SEARCH_PATH}?{params}")
    companies = _extract_list(payload, "companies", "data", "results")

    normalized_slug = COMPANY_SLUG.lower()
    for company in companies:
        shortname = str(company.get("shortname", "")).lower()
        name = str(company.get("name", "")).lower()
        if shortname == normalized_slug or "localiza meoo" in name:
            company_id = company.get("id")
            if company_id:
                return str(company_id)

    raise ReclameAquiCollectionError(
        "Não foi possível resolver o company_id público da Localiza Meoo "
        "no endpoint do Reclame AQUI."
    )


def fetch_complaints_page(
    page: int,
    *,
    company_id: str,
    per_page: int = DEFAULT_PER_PAGE,
) -> dict[str, Any]:
    if page < 0:
        raise ValueError("A página do Reclame AQUI deve ser >= 0.")
    if not 1 <= per_page <= 10:
        raise ValueError("O Reclame AQUI limita o perPage público a 10.")

    params = urlencode(
        {
            "page": page,
            "perPage": per_page,
            "companyId": company_id,
        }
    )
    url = f"{BFF_BASE_URL}{COMPLAINTS_PATH}?{params}"
    payload = _request_json(url)
    return payload if isinstance(payload, dict) else {"complaints": []}


def _absolute_complaint_url(complaint_id: str, title: str) -> str:
    # The public BFF does not provide the canonical SEO slug. The ID is kept
    # in the query parameter so every record still points back to the company
    # listing even when the individual slug is unavailable.
    return f"{SOURCE_URL}?complaint_id={complaint_id}"


def normalize_complaints(payload: dict[str, Any]) -> pd.DataFrame:
    complaints = _extract_list(payload, "complaints")
    rows: list[dict[str, Any]] = []
    for complaint in complaints:
        complaint_id = complaint.get("id")
        if complaint_id is None:
            continue
        company = complaint.get("company") or {}
        title = str(complaint.get("title") or "").strip()
        description = str(complaint.get("description") or "").strip()
        rows.append(
            {
                "complaint_id": str(complaint_id),
                "title": title,
                "summary": description,
                "status": complaint.get("status"),
                "solved": complaint.get("solved"),
                "city": complaint.get("city"),
                "state": complaint.get("state"),
                "published_at": pd.to_datetime(
                    complaint.get("created"), errors="coerce"
                ),
                "source_url": _absolute_complaint_url(str(complaint_id), title),
                "company_id": str(company.get("id")) if company.get("id") else None,
                "company_name": company.get("name"),
                "company_shortname": company.get("shortname"),
                "data_origin": "EXTERNAL_PUBLIC",
                "collection_method": "RECLAME_AQUI_PUBLIC_BFF",
            }
        )

    frame = pd.DataFrame(rows, columns=REVIEW_COLUMNS)
    if frame.empty:
        return frame
    frame["published_at"] = pd.to_datetime(
        frame["published_at"], errors="coerce"
    ).dt.strftime("%Y-%m-%dT%H:%M:%S")
    return frame.drop_duplicates(subset=["complaint_id"])


def _load_progress() -> tuple[pd.DataFrame, set[str], int]:
    if not PROGRESS_PATH.exists() or not PROGRESS_META_PATH.exists():
        return pd.DataFrame(columns=REVIEW_COLUMNS), set(), 0

    progress = pd.read_csv(PROGRESS_PATH)
    if progress.empty:
        return progress, set(), 0

    try:
        meta = json.loads(PROGRESS_META_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        meta = {}

    seen_ids = (
        set(progress["complaint_id"].astype(str).tolist())
        if "complaint_id" in progress.columns
        else set()
    )
    next_page = int(meta.get("next_page", 0))
    return progress, seen_ids, next_page


def _save_progress(frame: pd.DataFrame, *, next_page: int, company_id: str) -> None:
    PROGRESS_PATH.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(PROGRESS_PATH, index=False, quoting=csv.QUOTE_MINIMAL)
    PROGRESS_META_PATH.write_text(
        json.dumps(
            {
                "company_id": company_id,
                "next_page": next_page,
                "records": int(len(frame)),
                "saved_at": pd.Timestamp.utcnow().isoformat(),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )


def _clear_progress() -> None:
    for path in (PROGRESS_PATH, PROGRESS_META_PATH):
        try:
            path.unlink()
        except FileNotFoundError:
            pass


def collect_all_complaints(
    *,
    company_id: str | None = None,
    per_page: int = DEFAULT_PER_PAGE,
    max_pages: int | None = None,
    delay_seconds: float = DEFAULT_DELAY_SECONDS,
    resume: bool = False,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    resolved_company_id = company_id or resolve_company_id()

    if resume:
        progress_frame, seen_ids, page = _load_progress()
    else:
        _clear_progress()
        progress_frame = pd.DataFrame(columns=REVIEW_COLUMNS)
        seen_ids = set()
        page = 0

    frames: list[pd.DataFrame] = [progress_frame] if not progress_frame.empty else []
    pages_fetched = page
    completed = False
    blocked_page: int | None = None
    error_message: str | None = None

    while max_pages is None or pages_fetched < max_pages:
        try:
            payload = fetch_complaints_page(
                page,
                company_id=resolved_company_id,
                per_page=per_page,
            )
        except ReclameAquiCollectionError as exc:
            blocked_page = page
            error_message = str(exc)
            partial = (
                pd.concat(frames, ignore_index=True, sort=False)
                if frames
                else pd.DataFrame(columns=REVIEW_COLUMNS)
            )
            _save_progress(
                partial.drop_duplicates("complaint_id"),
                next_page=page,
                company_id=resolved_company_id,
            )
            logger.error(
                "Reclame AQUI | coleta interrompida na página %s | registros preservados=%s",
                page,
                len(seen_ids),
            )
            break

        frame = normalize_complaints(payload)
        pages_fetched += 1

        if frame.empty:
            logger.info("Reclame AQUI | página %s vazia; encerrando", page)
            completed = True
            break

        new_mask = ~frame["complaint_id"].astype(str).isin(seen_ids)
        new_frame = frame.loc[new_mask].copy()
        if not new_frame.empty:
            seen_ids.update(new_frame["complaint_id"].astype(str).tolist())
            frames.append(new_frame)

        logger.info(
            "Reclame AQUI | página %s | página=%s | novos=%s | total acumulado=%s",
            page,
            len(frame),
            len(new_frame),
            len(seen_ids),
        )

        accumulated = pd.concat(frames, ignore_index=True, sort=False).drop_duplicates(
            "complaint_id"
        )
        _save_progress(
            accumulated,
            next_page=page + 1,
            company_id=resolved_company_id,
        )

        if len(frame) < per_page:
            completed = True
            break

        page += 1
        if delay_seconds > 0:
            jitter = random.uniform(0.25, 0.75)
            time.sleep(delay_seconds + jitter)

    if frames:
        result = pd.concat(frames, ignore_index=True, sort=False)
        result = result.drop_duplicates("complaint_id")
        result = result.sort_values("published_at", ascending=False, na_position="last")
    else:
        result = pd.DataFrame(columns=REVIEW_COLUMNS)

    metadata = {
        "company_id": resolved_company_id,
        "pages_fetched": pages_fetched,
        "complaints_collected": int(len(result)),
        "per_page": per_page,
        "collection_method": "RECLAME_AQUI_PUBLIC_BFF",
        "source_url": SOURCE_URL,
        "collected_on": pd.Timestamp.utcnow().strftime("%Y-%m-%dT%H:%M:%S%z"),
        "completed": completed,
        "resumed": resume,
        "blocked_page": blocked_page,
        "error": error_message,
        "next_page": page if blocked_page is not None else page + 1,
    }
    return result, metadata


def save_complaints(df: pd.DataFrame, *, output_path: str | Path = OUTPUT_PATH) -> Path:
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(destination, index=False, quoting=csv.QUOTE_MINIMAL)
    return destination


def write_snapshot(
    metadata: dict[str, Any], *, snapshot_path: str | Path = SNAPSHOT_PATH
) -> Path:
    destination = Path(snapshot_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    rows = [{"metric": key, "value": value} for key, value in metadata.items()]
    pd.DataFrame(rows).to_csv(destination, index=False)
    return destination


def collect_and_save_all(
    *,
    max_pages: int | None = None,
    per_page: int = DEFAULT_PER_PAGE,
    delay_seconds: float = DEFAULT_DELAY_SECONDS,
    resume: bool = False,
) -> tuple[Path, Path, dict[str, Any]]:
    frame, metadata = collect_all_complaints(
        max_pages=max_pages,
        per_page=per_page,
        delay_seconds=delay_seconds,
        resume=resume,
    )
    if frame.empty:
        raise ReclameAquiCollectionError(
            "Nenhuma reclamação foi coletada do Reclame AQUI."
        )
    output = save_complaints(frame)
    snapshot = write_snapshot(metadata)
    if metadata.get("completed"):
        _clear_progress()
    return output, snapshot, metadata


# Backwards-compatible helpers for the existing project/tests.
def _load_snapshot(path: str | Path) -> pd.DataFrame:
    source = Path(path)
    if not source.exists():
        raise FileNotFoundError(source)
    if source.suffix.lower() == ".csv":
        return pd.read_csv(source)
    if source.suffix.lower() in {".json", ".jsonl"}:
        return pd.read_json(source, lines=source.suffix.lower() == ".jsonl")
    raise ValueError("O snapshot precisa ser CSV, JSON ou JSONL")


def _validate(df: pd.DataFrame) -> pd.DataFrame:
    required = {
        "complaint_id",
        "title",
        "summary",
        "status",
        "city",
        "state",
        "published_at",
        "source_url",
    }
    missing = sorted(required.difference(df.columns))
    if missing:
        raise ValueError(f"Colunas obrigatórias ausentes: {', '.join(missing)}")

    result = df.copy()
    result["source"] = "RECLAME_AQUI"
    result["data_origin"] = result.get("data_origin", "EXTERNAL_PUBLIC")
    result["collection_method"] = result.get("collection_method", "PUBLIC_WEB_SNAPSHOT")
    result["published_at"] = pd.to_datetime(
        result["published_at"], errors="coerce"
    ).dt.strftime("%Y-%m-%dT%H:%M:%S")
    result["complaint_id"] = result["complaint_id"].astype(str)
    return result.drop_duplicates(subset=["complaint_id"])


def save_snapshot(
    snapshot_path: str | Path, output_path: str | Path = OUTPUT_PATH
) -> Path:
    df = _validate(_load_snapshot(snapshot_path))
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(destination, index=False, quoting=csv.QUOTE_MINIMAL)
    return destination


def fetch_public_page(url: str = SOURCE_URL) -> str:
    request = Request(
        url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                "Chrome/140.0 Safari/537.36"
            )
        },
    )
    with urlopen(request, timeout=30) as response:  # nosec B310
        return response.read().decode("utf-8", errors="replace")


def refresh_from_public_page(url: str = SOURCE_URL) -> Path:
    html = fetch_public_page(url)
    if (
        "lista de reclamações" not in html.lower()
        and "lista de reclamacoes" not in html.lower()
    ):
        raise ValueError(
            "A página pública não retornou um HTML reconhecível do Reclame AQUI."
        )
    raise ValueError(
        "A listagem HTML é dinâmica. Use `localiza reclameaqui` para coletar "
        "a base paginada através do endpoint público utilizado pelo site."
    )
