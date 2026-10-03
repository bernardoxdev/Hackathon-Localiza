from __future__ import annotations

from pathlib import Path

import pandas as pd

from app.core.data import DATA_DIR
from app.services.appstore_analysis import analyze_reviews, build_appstore_insights

INPUT_PATH = DATA_DIR / "appstore" / "app_store_reviews.csv"
OUTPUT_PATH = DATA_DIR / "appstore" / "review_analysis.csv"
INSIGHTS_PATH = DATA_DIR / "appstore" / "review_insights.csv"


def run_pipeline(
    *, input_path: Path | None = None, output_path: Path | None = None
) -> tuple[Path, Path, pd.DataFrame]:
    source = pd.read_csv(input_path or INPUT_PATH)
    analyzed = analyze_reviews(source)
    insights = build_appstore_insights(analyzed)

    output = output_path or OUTPUT_PATH
    output.parent.mkdir(parents=True, exist_ok=True)
    INSIGHTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    analyzed.to_csv(output, index=False)
    insights.to_csv(INSIGHTS_PATH, index=False)
    return output, INSIGHTS_PATH, analyzed
