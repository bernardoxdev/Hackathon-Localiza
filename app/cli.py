import argparse
import logging

import uvicorn

from app.ingest.appstore_pipeline import run_pipeline as run_appstore_pipeline
from app.ingest.appstore_reviews import (
    create_preview_dataset,
    write_snapshot,
)
from app.ingest.appstore_reviews import (
    create_reviews as create_appstore_reviews,
)
from app.ingest.googleplay_reviews import create_reviews
from app.ingest.reclameaqui import collect_and_save_all
from app.ingest.reclameaqui_pipeline import run_pipeline as run_reclameaqui_pipeline
from app.ingest.review_pipeline import run_pipeline

logger = logging.getLogger(__name__)


def criar_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="CLI do Hackathon Localiza.",
    )

    subparsers = parser.add_subparsers(
        dest="comando",
        required=True,
    )

    ingest_parser = subparsers.add_parser(
        "ingest",
        help="Importa reviews do Google Play.",
    )

    review_pipeline = subparsers.add_parser(
        "review", help="Analisa as reviews ingeridas e gera os artefatos da pipeline."
    )

    appstore_pipeline = subparsers.add_parser(
        "appstore",
        help="Importa e analisa reviews da Apple App Store.",
    )

    appstore_pipeline.add_argument("--country", default="br", help="País da App Store.")
    appstore_pipeline.add_argument(
        "--pages", type=int, default=10, help="Número de páginas do feed RSS."
    )
    appstore_pipeline.add_argument(
        "--preview",
        action="store_true",
        help="Gera preview público quando o feed live não estiver disponível.",
    )

    reclameaqui_pipeline = subparsers.add_parser(
        "reclameaqui",
        help="Coleta a base paginada pública do Reclame AQUI e gera os artefatos.",
    )
    reclameaqui_pipeline.add_argument(
        "--pages",
        type=int,
        default=0,
        help="Máximo de páginas. 0 = todas as páginas disponíveis.",
    )
    reclameaqui_pipeline.add_argument(
        "--per-page",
        type=int,
        default=10,
        choices=range(1, 11),
        help="Registros por página (máximo público: 10).",
    )
    reclameaqui_pipeline.add_argument(
        "--delay",
        type=float,
        default=1.2,
        help="Intervalo mínimo entre páginas, em segundos. Use pelo menos 1.0 para reduzir bloqueios.",
    )
    reclameaqui_pipeline.add_argument(
        "--resume",
        action="store_true",
        help="Retoma a coleta do último checkpoint salvo após bloqueio/falha.",
    )
    reclameaqui_pipeline.add_argument(
        "--use-existing",
        action="store_true",
        help="Não coleta da web; apenas reprocessa o CSV existente.",
    )

    run_parser = subparsers.add_parser(
        "run",
        help="Inicia a API do Hackathon Localiza.",
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


def executar_reclameaqui(
    *, max_pages: int, per_page: int, delay: float, use_existing: bool, resume: bool
) -> None:
    if not use_existing:
        output, snapshot, metadata = collect_and_save_all(
            max_pages=max_pages or None,
            per_page=per_page,
            delay_seconds=delay,
            resume=resume,
        )
        print(f"Reclamações coletadas: {metadata['complaints_collected']}")
        print(f"Páginas coletadas: {metadata['pages_fetched']}")
        print(f"Dados: {output}")
        print(f"Snapshot: {snapshot}")

        if not metadata.get("completed", False):
            print(
                "ATENÇÃO: a coleta foi interrompida antes do fim. "
                f"Página bloqueada: {metadata.get('blocked_page')}. "
                "O checkpoint foi preservado. Execute novamente com --resume "
                "após o bloqueio esfriar."
            )

    analysis_path, insights_path, analyzed = run_reclameaqui_pipeline()
    print(f"Reclamações analisadas: {len(analyzed)}")
    print(f"Saída: {analysis_path}")
    print(f"Insights: {insights_path}")


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

        elif args.comando == "reclameaqui":
            executar_reclameaqui(
                max_pages=args.pages,
                per_page=args.per_page,
                delay=args.delay,
                use_existing=args.use_existing,
                resume=args.resume,
            )

        elif args.comando == "appstore":
            try:
                create_appstore_reviews(country=args.country, pages=args.pages)
                write_snapshot()
            except RuntimeError:
                if not args.preview:
                    raise
                create_preview_dataset()
                write_snapshot()
            output, insights, analyzed = run_appstore_pipeline()
            print(f"App Store analisadas: {len(analyzed)}")
            print(f"Saída: {output}")
            print(f"Insights: {insights}")

    except (FileNotFoundError, ValueError) as erro:
        parser.error(str(erro))


if __name__ == "__main__":
    main()
