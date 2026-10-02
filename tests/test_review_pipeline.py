from pathlib import Path

import pandas as pd

from app.ingest.review_pipeline import analyze_reviews, build_insights, normalize_text, run_pipeline


BASE = Path(__file__).resolve().parents[1]
REVIEWS = BASE / "data" / "googleplay" / "google_play_reviews.csv"


def test_normalize_text():
    assert normalize_text("Ótimo app!!!") == "otimo app"


def test_analysis_creates_context_fields():
    source = pd.read_csv(REVIEWS).head(20)
    analyzed = analyze_reviews(source)
    expected = {
        "sentiment",
        "topic",
        "journey_moment",
        "pain_category",
        "urgency",
        "context_opportunity",
        "recommended_action",
        "confidence",
        "matched_signals",
    }
    assert expected.issubset(analyzed.columns)
    assert len(analyzed) == len(source)
    assert analyzed["sentiment"].notna().all()


def test_known_maintenance_signal_is_classified():
    source = pd.DataFrame(
        [
            {
                "review_id": "x1",
                "rating": 1,
                "review_text": "Não consigo agendar a revisão, o aplicativo não permite selecionar a cidade.",
                "review_date": "2026-09-01",
                "app_version": "5.1.1",
                "thumbs_up_count": 0,
                "reply_content": None,
                "data_origin": "GOOGLE_PLAY",
            }
        ]
    )
    analyzed = analyze_reviews(source).iloc[0]
    assert analyzed["sentiment"] == "negativo"
    assert analyzed["topic"] == "manutencao_agendamento"
    assert analyzed["pain_category"] == "erro_funcional"
    assert analyzed["context_opportunity"] == "proactive_care"
    assert analyzed["recommended_action"] == "Agendar revisão"


def test_build_insights_returns_dimensions():
    source = pd.read_csv(REVIEWS).head(50)
    analyzed = analyze_reviews(source)
    insights = build_insights(analyzed)
    assert set(insights["dimension"].unique()) == {
        "sentiment",
        "topic",
        "journey_moment",
        "pain_category",
        "context_opportunity",
    }


def test_pipeline_generates_artifacts(tmp_path):
    source = pd.read_csv(REVIEWS).head(12)
    input_path = tmp_path / "reviews.csv"
    output_path = tmp_path / "review_analysis.csv"
    source.to_csv(input_path, index=False)

    result_path, insights_path, analyzed = run_pipeline(
        input_path=input_path,
        output_path=output_path,
    )

    assert result_path == output_path
    assert insights_path.exists()
    assert output_path.exists()
    assert len(analyzed) == 12
