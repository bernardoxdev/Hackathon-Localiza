import argparse
import logging

import uvicorn

from app.ingest.googleplay_reviews import create_reviews
from app.ingest.review_pipeline import run_pipeline

logger = logging.getLogger(__name__)


def criar_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="CLI do BrandPulse.",
    )

    subparsers = parser.add_subparsers(
        dest="comando",
        required=True,
    )

    ingest_parser = subparsers.add_parser(
        "ingest",
        help="Importa respostas de um arquivo JSON.",
    )

    review_pipeline = subparsers.add_parser(
        "review",
        help="Faz o review dos dados gerados pelo ingest"
    )

    run_parser = subparsers.add_parser(
        "run",
        help="Inicia a API do BrandPulse.",
    )

    run_parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host onde a API será executada.",
    )

    run_parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Porta onde a API será executada.",
    )

    run_parser.add_argument(
        "--reload",
        action="store_true",
        help="Ativa o hot reload durante o desenvolvimento.",
    )

    return parser


def executar_ingestao() -> None:
    create_reviews()


def executar_api(host: str, port: int, reload: bool) -> None:
    uvicorn.run("app.main:app", host=host, port=port, reload=reload)


def executar_review() -> None:
    review_path, insights_path, analyzed = run_pipeline()
    print(f"Reviews analisadas: {len(analyzed)}")
    print(f"Saída: {review_path}")
    print(f"Insights: {insights_path}")

def main() -> None:
    parser = criar_parser()
    args = parser.parse_args()

    try:
        if args.comando == "ingest":
            executar_ingestao()

        elif args.comando == "run":
            executar_api(host=args.host, port=args.port, reload=args.reload)

        elif args.comando == "review":
            executar_review()


    except (FileNotFoundError, ValueError) as erro:
        parser.error(str(erro))


if __name__ == "__main__":
    main()
