from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd

from app.core.data import DATA_DIR, json_safe

TOKEN_RE = re.compile(r"[\wÀ-ÿ]+", re.UNICODE)

# Palavras de baixo valor para a recuperação lexical. O identificador do cliente
# e os metadados do carro continuam sendo filtros estruturais e não dependem
# desta lista.
STOPWORDS = {
    "a",
    "ao",
    "aos",
    "as",
    "com",
    "como",
    "da",
    "das",
    "de",
    "do",
    "dos",
    "e",
    "em",
    "eu",
    "me",
    "na",
    "nas",
    "no",
    "nos",
    "o",
    "os",
    "para",
    "por",
    "que",
    "se",
    "sem",
    "sobre",
    "um",
    "uma",
    "umas",
    "uns",
    "vou",
    "quero",
    "preciso",
    "pode",
    "posso",
    "tem",
    "tenho",
    "minha",
    "meu",
    "minhas",
    "meus",
    "isso",
    "esta",
    "está",
    "estao",
    "estão",
    "ser",
    "vai",
    "mais",
    "muito",
}


@dataclass(frozen=True, slots=True)
class RAGDocument:
    """Documento recuperável pelo RAG."""

    document_id: str
    source: str
    text: str
    metadata: dict[str, Any]
    score: float


@dataclass(frozen=True, slots=True)
class RAGResult:
    """Resultado de uma recuperação contextual."""

    customer_id: str
    vehicle_id: str
    vehicle_type: str
    query: str
    documents: list[RAGDocument]

    @property
    def context_text(self) -> str:
        if not self.documents:
            return "Nenhum dado contextual foi recuperado."

        sections: list[str] = []
        for document in self.documents:
            sections.append(
                f"[{document.source} | {document.document_id}]\n{document.text}"
            )
        return "\n\n".join(sections)

    def as_dict(self) -> dict[str, Any]:
        return {
            "customer_id": self.customer_id,
            "vehicle_id": self.vehicle_id,
            "vehicle_type": self.vehicle_type,
            "query": self.query,
            "document_count": len(self.documents),
            "documents": [
                {
                    "document_id": document.document_id,
                    "source": document.source,
                    "score": round(document.score, 4),
                    "metadata": document.metadata,
                    "text": document.text,
                }
                for document in self.documents
            ],
        }


class CustomerRAG:
    """RAG determinístico com filtros por cliente e veículo.

    Para este protótipo, os dados são estruturados em CSV. Em vez de criar um
    vetor genérico para tudo, a recuperação começa por metadados confiáveis:

    1. customer_id é obrigatório;
    2. o contrato relaciona o cliente ao vehicle_id;
    3. o tipo/modelo/categoria do veículo é usado como contexto de recuperação;
    4. apenas registros do cliente e do veículo associado podem entrar no
       contexto final;
    5. dentro desse universo filtrado, uma pontuação lexical prioriza os
       registros relacionados à pergunta.

    Isso reduz o risco de misturar dados de clientes diferentes, que é a regra
    mais importante para o assistente.
    """

    DATASETS = {
        "clients": "clients.csv",
        "contracts": "contracts.csv",
        "vehicles": "vehicles.csv",
        "telemetry": "telemetry.csv",
        "maintenance": "maintenance.csv",
        "trips": "trips.csv",
        "context_events": "context_events.csv",
        "recommendations": "recommendations.csv",
        "app_events": "app_events.csv",
    }

    def __init__(self, data_dir: Path | None = None) -> None:
        self.data_dir = data_dir or DATA_DIR
        self._frames: dict[str, pd.DataFrame] = {}
        self._load()

    def _load(self) -> None:
        for name, filename in self.DATASETS.items():
            path = self.data_dir / filename
            if path.exists():
                self._frames[name] = pd.read_csv(path)
            else:
                self._frames[name] = pd.DataFrame()

    def _df(self, name: str) -> pd.DataFrame:
        return self._frames.get(name, pd.DataFrame())

    def _customer_row(self, customer_id: str) -> pd.Series:
        df = self._df("clients")
        match = df[df["customer_id"].astype(str) == str(customer_id)]
        if match.empty:
            raise ValueError(f"Cliente não encontrado: {customer_id}")
        return match.iloc[0]

    def _contract_row(self, customer_id: str) -> pd.Series:
        df = self._df("contracts")
        match = df[df["customer_id"].astype(str) == str(customer_id)]
        if match.empty:
            raise ValueError(f"Contrato não encontrado para {customer_id}")
        return match.sort_values("start_date").iloc[-1]

    def _vehicle_row(self, vehicle_id: str) -> pd.Series:
        df = self._df("vehicles")
        match = df[df["vehicle_id"].astype(str) == str(vehicle_id)]
        if match.empty:
            raise ValueError(f"Veículo não encontrado: {vehicle_id}")
        return match.iloc[0]

    @staticmethod
    def _tokenize(text: str) -> set[str]:
        tokens = {token.lower() for token in TOKEN_RE.findall(str(text))}
        return {token for token in tokens if token not in STOPWORDS and len(token) > 2}

    def _vehicle_document(self, customer_id: str, vehicle: pd.Series) -> RAGDocument:
        text = (
            f"Veículo {vehicle.get('vehicle_id')}: fabricante={vehicle.get('make')}, "
            f"modelo={vehicle.get('model')}, versão={vehicle.get('version')}, "
            f"ano={vehicle.get('year')}, categoria={vehicle.get('category')}, "
            f"powertrain={vehicle.get('powertrain')}, combustível={vehicle.get('fuel_type')}, "
            f"potência_hp={vehicle.get('power_hp')}, consumo={vehicle.get('avg_consumption')} "
            f"{vehicle.get('consumption_unit')}, autonomia_estimada_km={vehicle.get('estimated_range_km')}, "
            f"passageiros={vehicle.get('passengers')}, porta_malas_l={vehicle.get('trunk_l')}, "
            f"transmissão={vehicle.get('transmission')}, arquétipo_mobilidade={vehicle.get('mobility_archetype')}."
        )
        return RAGDocument(
            document_id=f"vehicle:{vehicle.get('vehicle_id')}",
            source="vehicle_profile",
            text=text,
            metadata={
                "customer_id": customer_id,
                "vehicle_id": json_safe(vehicle.get("vehicle_id")),
                "vehicle_type": json_safe(vehicle.get("category")),
                "model": json_safe(vehicle.get("model")),
            },
            score=99.0,
        )

    @staticmethod
    def _row_text(row: pd.Series, fields: list[str]) -> str:
        parts = []
        for field in fields:
            if field in row.index and pd.notna(row[field]):
                parts.append(f"{field}={json_safe(row[field])}")
        return "; ".join(parts)

    def _latest_records(
        self,
        name: str,
        filters: dict[str, Any],
        date_columns: list[str],
        limit: int,
    ) -> pd.DataFrame:
        df = self._df(name)
        if df.empty:
            return df
        result = df.copy()
        for field, value in filters.items():
            if field not in result.columns:
                continue
            result = result[result[field].astype(str) == str(value)]
        if result.empty:
            return result
        for column in date_columns:
            if column in result.columns:
                result[column] = pd.to_datetime(result[column], errors="coerce")
                result = result.sort_values(column, ascending=False)
                break
        return result.head(limit)

    def _summary_document(
        self,
        customer: pd.Series,
        contract: pd.Series,
        vehicle: pd.Series,
        telemetry: pd.DataFrame,
        maintenance: pd.DataFrame,
    ) -> RAGDocument:
        t = telemetry.iloc[0] if not telemetry.empty else pd.Series(dtype=object)
        m = maintenance.iloc[0] if not maintenance.empty else pd.Series(dtype=object)
        text = (
            f"Cliente {customer.get('customer_id')}: perfil={customer.get('profile')}, "
            f"cidade={customer.get('city')}/{customer.get('state')}, "
            f"canal={customer.get('preferred_channel')}.\n"
            f"Contrato {contract.get('contract_id')}: status={contract.get('status')}, "
            f"meses_restantes={contract.get('months_remaining')}, "
            f"franquia_km={contract.get('monthly_km_allowance')}, "
            f"renovacao={contract.get('renewal_date')}.\n"
            f"Veículo {vehicle.get('vehicle_id')}: {vehicle.get('make')} "
            f"{vehicle.get('model')} {vehicle.get('version')}, ano={vehicle.get('year')}, "
            f"categoria={vehicle.get('category')}, powertrain={vehicle.get('powertrain')}, "
            f"combustivel={vehicle.get('fuel_type')}, arquétipo={vehicle.get('mobility_archetype')}.\n"
            f"Telemetria mais recente: km_usado_mes={t.get('km_used_month')}, "
            f"km_disponivel={t.get('km_available')}, "
            f"utilizacao={t.get('franchise_utilization_pct')}%, "
            f"status_veiculo={t.get('vehicle_status')}, "
            f"km_para_manutencao={t.get('maintenance_km_remaining')}.\n"
            f"Manutenção mais recente: tipo={m.get('maintenance_type')}, "
            f"classe={m.get('maintenance_class')}, km_restantes={m.get('km_remaining')}, "
            f"status={m.get('status')}, oficina={m.get('workshop_name')}."
        )
        return RAGDocument(
            document_id=f"customer:{customer.get('customer_id')}",
            source="customer_context",
            text=text,
            metadata={
                "customer_id": json_safe(customer.get("customer_id")),
                "vehicle_id": json_safe(vehicle.get("vehicle_id")),
                "vehicle_type": json_safe(vehicle.get("category")),
                "model": json_safe(vehicle.get("model")),
            },
            score=100.0,
        )

    def retrieve(
        self,
        customer_id: str,
        query: str,
        top_k: int = 8,
    ) -> RAGResult:
        customer = self._customer_row(customer_id)
        contract = self._contract_row(customer_id)
        vehicle_id = str(contract.get("vehicle_id"))
        vehicle = self._vehicle_row(vehicle_id)

        telemetry = self._latest_records(
            "telemetry",
            {"customer_id": customer_id, "vehicle_id": vehicle_id},
            ["timestamp"],
            3,
        )
        maintenance = self._latest_records(
            "maintenance",
            {"customer_id": customer_id, "vehicle_id": vehicle_id},
            ["event_date"],
            3,
        )

        documents: list[RAGDocument] = [
            self._summary_document(
                customer,
                contract,
                vehicle,
                telemetry,
                maintenance,
            ),
            self._vehicle_document(customer_id, vehicle),
        ]

        query_tokens = self._tokenize(
            f"{query} {vehicle.get('category', '')} {vehicle.get('model', '')} "
            f"{vehicle.get('make', '')} {vehicle.get('mobility_archetype', '')}"
        )

        candidate_specs = [
            (
                "telemetry",
                telemetry,
                [
                    "timestamp",
                    "odometer_km",
                    "km_used_month",
                    "monthly_km_allowance",
                    "km_available",
                    "franchise_utilization_pct",
                    "avg_speed_kmh",
                    "avg_trip_distance_km",
                    "trip_count_30d",
                    "fuel_level_pct",
                    "battery_level_pct",
                    "estimated_range_km",
                    "city_region",
                    "vehicle_status",
                    "alert_type",
                    "maintenance_km_remaining",
                ],
                "timestamp",
            ),
            (
                "maintenance",
                maintenance,
                [
                    "event_date",
                    "maintenance_type",
                    "maintenance_class",
                    "odometer_km",
                    "next_maintenance_km",
                    "km_remaining",
                    "workshop_name",
                    "status",
                    "tire_status",
                    "oil_status",
                    "battery_status",
                    "brake_status",
                ],
                "event_date",
            ),
            (
                "trips",
                self._latest_records(
                    "trips",
                    {"customer_id": customer_id, "vehicle_id": vehicle_id},
                    ["trip_date"],
                    20,
                ),
                [
                    "trip_date",
                    "start_time",
                    "origin_city",
                    "destination_city",
                    "distance_km",
                    "duration_min",
                    "purpose",
                    "route_type",
                    "recurring_route",
                    "long_trip_flag",
                    "day_of_week",
                ],
                "trip_date",
            ),
            (
                "context_events",
                self._latest_records(
                    "context_events",
                    {"customer_id": customer_id, "vehicle_id": vehicle_id},
                    ["timestamp"],
                    20,
                ),
                [
                    "timestamp",
                    "context_type",
                    "maintenance_soon",
                    "contract_renewal_soon",
                    "benefit_available",
                    "long_trip_pattern",
                    "support_need_signal",
                    "context_priority",
                ],
                "timestamp",
            ),
            (
                "recommendations",
                self._latest_records(
                    "recommendations",
                    {"customer_id": customer_id, "vehicle_id": vehicle_id},
                    ["generated_at"],
                    20,
                ),
                [
                    "created_at",
                    "recommendation_type",
                    "title",
                    "description",
                    "priority",
                    "status",
                ],
                "created_at",
            ),
            (
                "app_events",
                self._latest_records(
                    "app_events",
                    {"customer_id": customer_id, "vehicle_id": vehicle_id},
                    ["timestamp"],
                    20,
                ),
                ["timestamp", "feature", "event_type", "screen", "source"],
                "timestamp",
            ),
        ]

        for source, frame, fields, _date_field in candidate_specs:
            if frame.empty:
                continue

            for index, row in frame.iterrows():
                text = self._row_text(row, fields)
                tokens = self._tokenize(text)
                overlap = len(query_tokens & tokens)
                score = 1.0 + overlap

                # Termos específicos do veículo recebem um peso extra. O filtro
                # estrutural já garante que o registro pertence ao cliente;
                # aqui nós apenas aumentamos a relevância quando a pergunta
                # mencionar o tipo/modelo do carro.
                vehicle_tokens = self._tokenize(
                    f"{vehicle.get('category', '')} {vehicle.get('model', '')} "
                    f"{vehicle.get('make', '')} {vehicle.get('mobility_archetype', '')}"
                )
                vehicle_overlap = len(query_tokens & vehicle_tokens)
                score += vehicle_overlap * 1.5

                documents.append(
                    RAGDocument(
                        document_id=f"{source}:{index}",
                        source=source,
                        text=text,
                        metadata={
                            "customer_id": customer_id,
                            "vehicle_id": vehicle_id,
                            "vehicle_type": json_safe(vehicle.get("category")),
                            "model": json_safe(vehicle.get("model")),
                        },
                        score=float(score),
                    )
                )

        # O resumo principal sempre permanece. Os demais documentos entram por
        # relevância e depois por ordem de score.
        summary = documents[0]
        ranked = sorted(documents[1:], key=lambda doc: doc.score, reverse=True)
        selected = [summary, *ranked[: max(0, top_k - 1)]]

        return RAGResult(
            customer_id=customer_id,
            vehicle_id=vehicle_id,
            vehicle_type=str(vehicle.get("category", "")),
            query=query,
            documents=selected,
        )


customer_rag = CustomerRAG()
