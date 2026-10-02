from __future__ import annotations

from typing import Any

import pandas as pd
from fastapi import APIRouter, Query

from app.core.data import (
    DATASET_LABELS,
    DATASETS,
    dataset_or_404,
    load_dataset,
    records,
)

router = APIRouter(prefix="/api/datasets", tags=["Datasets"])


@router.get("")
def list_datasets() -> list[dict[str, Any]]:
    output = []
    for name, filename in DATASETS.items():
        df = load_dataset(name)
        output.append(
            {
                "name": name,
                "label": DATASET_LABELS.get(name, name),
                "rows": int(len(df)),
                "columns": int(len(df.columns)),
                "origin": sorted(
                    df["data_origin"].dropna().astype(str).unique().tolist()
                )
                if "data_origin" in df.columns
                else [],
                "filename": filename,
            }
        )
    return output


@router.get("/{name}")
def get_dataset(
    name: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
    q: str = Query(""),
) -> dict[str, Any]:
    df = dataset_or_404(name).copy()
    if q.strip():
        q = q.strip().lower()
        mask = pd.Series(False, index=df.index)
        for col in df.columns:
            mask = mask | df[col].astype(str).str.lower().str.contains(q, na=False)
        df = df.loc[mask]

    total = len(df)
    start = (page - 1) * page_size
    end = start + page_size
    page_df = df.iloc[start:end]

    return {
        "name": name,
        "label": DATASET_LABELS.get(name, name),
        "total": int(total),
        "page": page,
        "page_size": page_size,
        "columns": [{"name": c, "dtype": str(df[c].dtype)} for c in df.columns],
        "rows": records(page_df),
    }
