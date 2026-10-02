from __future__ import annotations

from typing import Any

import pandas as pd
from fastapi import APIRouter

from app.core.data import DATASET_LABELS, dataset_or_404, load_dataset

router = APIRouter(prefix="/api/metadata", tags=["Metadata"])


@router.get("/{name}")
def metadata(name: str) -> dict[str, Any]:
    df = dataset_or_404(name)
    dictionary = load_dataset("data_dictionary")
    subset = (
        dictionary[dictionary.dataset.eq(name)]
        if "dataset" in dictionary.columns
        else pd.DataFrame()
    )

    cols = []
    for col in df.columns:
        row = subset[subset.column.eq(col)] if not subset.empty else pd.DataFrame()
        info = row.iloc[0].to_dict() if not row.empty else {}
        cols.append(
            {
                "name": col,
                "dtype": str(df[col].dtype),
                "type": info.get("type"),
                "unit": info.get("unit"),
                "origin": info.get("origin"),
                "description": info.get("description"),
            }
        )

    return {"name": name, "label": DATASET_LABELS.get(name, name), "columns": cols}
