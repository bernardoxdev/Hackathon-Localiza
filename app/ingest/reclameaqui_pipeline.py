from __future__ import annotations

from pathlib import Path

import pandas as pd

from app.core.data import DATA_DIR
from app.services.reclameaqui_analysis import analyze_complaints

INPUT_PATH = DATA_DIR / "reclameaqui" / "reclameaqui_complaints.csv"
OUTPUT_PATH = DATA_DIR / "reclameaqui" / "complaint_analysis.csv"
INSIGHTS_PATH = DATA_DIR / "reclameaqui" / "complaint_insights.csv"


def run_pipeline(input_path: Path = INPUT_PATH) -> tuple[Path, Path, pd.DataFrame]:
    df = pd.read_csv(input_path)
    analyzed = analyze_complaints(df)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    analyzed.to_csv(OUTPUT_PATH, index=False)

    total = max(len(analyzed), 1)
    grouped_frames = []
    for dimension in [
        "topic",
        "journey_moment",
        "pain_category",
        "context_opportunity",
        "status",
    ]:
        grouped = (
            analyzed.groupby(dimension, dropna=False)
            .agg(complaint_count=("complaint_id", "count"))
            .reset_index()
            .rename(columns={dimension: "label"})
        )
        grouped.insert(0, "dimension", dimension)
        grouped["share_pct"] = (grouped["complaint_count"] / total * 100).round(1)
        grouped_frames.append(
            grouped[["dimension", "label", "complaint_count", "share_pct"]]
        )

    pd.concat(grouped_frames, ignore_index=True).to_csv(INSIGHTS_PATH, index=False)
    return OUTPUT_PATH, INSIGHTS_PATH, analyzed
