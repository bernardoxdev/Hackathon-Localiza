from __future__ import annotations

import logging
import time
from pathlib import Path

import pandas as pd
from google_play_scraper import Sort, reviews

APP_ID = "com.localiza.meoo.app"

BASE_DIR = Path(__file__).resolve().parents[2]
OUTPUT_DIR = BASE_DIR / "data" / "googleplay"
OUTPUT_FILE = OUTPUT_DIR / "google_play_reviews.csv"

LANGUAGE = "pt"
COUNTRY = "br"

BATCH_SIZE = 200
SLEEP_SECONDS = 2.0

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger("google-play-ingest")


def fetch_all_reviews() -> list[dict]:
    """
    Busca reviews usando paginação por continuation_token.
    """

    all_reviews: list[dict] = []
    continuation_token = None
    page = 0

    while True:
        page += 1

        logger.info(
            "Buscando página %d | acumuladas: %d",
            page,
            len(all_reviews),
        )

        try:
            result, continuation_token = reviews(
                APP_ID,
                lang=LANGUAGE,
                country=COUNTRY,
                sort=Sort.NEWEST,
                count=BATCH_SIZE,
                filter_score_with=None,
                continuation_token=continuation_token,
            )

        except Exception:
            logger.exception(
                "Erro ao consultar Google Play na página %d",
                page,
            )
            break

        if not result:
            logger.info("Google Play não retornou mais reviews.")
            break

        all_reviews.extend(result)

        logger.info(
            "Página %d trouxe %d reviews.",
            page,
            len(result),
        )

        if continuation_token is None:
            logger.info("Não existe continuation_token. Paginação encerrada.")
            break

        time.sleep(SLEEP_SECONDS)

    return all_reviews


def normalize_reviews(reviews_data: list[dict]) -> pd.DataFrame:
    """
    Normaliza os registros recebidos do Google Play.
    """

    rows = []

    for review in reviews_data:
        rows.append(
            {
                "review_id": review.get("reviewId"),
                "author_name": review.get("userName"),
                "rating": review.get("score"),
                "review_text": review.get("content"),
                "thumbs_up_count": review.get("thumbsUpCount"),
                "app_version": review.get("reviewCreatedVersion"),
                "review_date": review.get("at"),
                "reply_content": review.get("replyContent"),
                "reply_date": review.get("repliedAt"),
                "app_id": APP_ID,
                "language": LANGUAGE,
                "country": COUNTRY,
                "source": "google_play",
                "data_origin": "GOOGLE_PLAY",
            }
        )

    df = pd.DataFrame(rows)

    if df.empty:
        return df

    # Remove duplicações pelo ID oficial da review.
    df = df.drop_duplicates(
        subset=["review_id"],
        keep="first",
    )

    # Ordenação cronológica.
    df = df.sort_values(
        by="review_date",
        ascending=False,
    )

    return df


def save_reviews(df: pd.DataFrame) -> None:
    """
    Salva o dataset final.
    """

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    df.to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8-sig",
    )

    logger.info(
        "Arquivo salvo em: %s",
        OUTPUT_FILE,
    )


def create_reviews():
    logger.info(
        "Iniciando ingestão do Google Play: %s",
        APP_ID,
    )

    data = fetch_all_reviews()

    logger.info(
        "Total bruto coletado: %d",
        len(data),
    )

    df = normalize_reviews(data)

    logger.info(
        "Total após deduplicação: %d",
        len(df),
    )

    if df.empty:
        logger.warning("Nenhuma review foi encontrada.")
        return

    save_reviews(df)

    print("\n======================================")
    print("GOOGLE PLAY INGEST FINALIZADO")
    print("======================================")
    print(f"Reviews coletadas: {len(df):,}")
    print(f"Arquivo: {OUTPUT_FILE}")
    print("======================================\n")


if __name__ == "__main__":
    create_reviews()
