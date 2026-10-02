from __future__ import annotations

import math
from functools import cache
from pathlib import Path
from typing import Any

import pandas as pd
from fastapi import HTTPException

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"

DATASETS = {
    "vehicles": "vehicles.csv",
    "clients": "clients.csv",
    "contracts": "contracts.csv",
    "telemetry": "telemetry.csv",
    "trips": "trips.csv",
    "maintenance": "maintenance.csv",
    "app_events": "app_events.csv",
    "context_events": "context_events.csv",
    "recommendations": "recommendations.csv",
    "prototype_scenarios": "prototype_scenarios.csv",
    "data_dictionary": "data_dictionary.csv",
    "relationships": "relationships.csv",
    "insights_examples": "insights_examples.csv",
    "public_datasets": "public_datasets.csv",
    "googleplay_reviews": "googleplay/google_play_reviews.csv",
    "review_analysis": "googleplay/review_analysis.csv",
    "review_insights": "googleplay/review_insights.csv",
}

DATASET_LABELS = {
    "vehicles": "Veículos",
    "clients": "Clientes",
    "contracts": "Contratos",
    "telemetry": "Telemetria",
    "trips": "Viagens",
    "maintenance": "Manutenção",
    "app_events": "Eventos do App",
    "context_events": "Contexto",
    "recommendations": "Recomendações",
    "prototype_scenarios": "Cenários do Protótipo",
    "data_dictionary": "Dicionário de Dados",
    "relationships": "Relacionamentos",
    "insights_examples": "Insights de Exemplo",
    "public_datasets": "Datasets Públicos",
    "googleplay_reviews": "Reviews Google Play",
    "review_analysis": "Análise das Reviews",
    "review_insights": "Insights das Reviews",
}


def json_safe(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
        return None
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if hasattr(value, "item"):
        try:
            value = value.item()
        except Exception:
            pass
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if pd.isna(value) if not isinstance(value, (list, dict, tuple)) else False:
        return None
    return value


def records(df: pd.DataFrame) -> list[dict[str, Any]]:
    return [{k: json_safe(v) for k, v in row.items()} for row in df.to_dict(orient="records")]


@cache
def load_dataset(name: str) -> pd.DataFrame:
    filename = DATASETS.get(name)
    if not filename:
        raise KeyError(name)
    path = DATA_DIR / filename
    if not path.exists():
        raise FileNotFoundError(path)
    return pd.read_csv(path)


def dataset_or_404(name: str) -> pd.DataFrame:
    if name not in DATASETS:
        raise HTTPException(status_code=404, detail=f"Dataset desconhecido: {name}")
    return load_dataset(name)


def pct(v: float) -> float:
    return round(float(v), 1)


def latest_by(df: pd.DataFrame, key: str, date_col: str) -> pd.DataFrame:
    x = df.copy()
    x[date_col] = pd.to_datetime(x[date_col], errors="coerce")
    return x.sort_values(date_col).drop_duplicates(key, keep="last")
