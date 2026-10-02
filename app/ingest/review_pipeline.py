from __future__ import annotations

import re
import unicodedata
from pathlib import Path
from typing import Any

import pandas as pd

from app.core.data import DATA_DIR, load_dataset
from app.services.review_analysis import ANALYSIS_COLUMNS

PIPELINE_VERSION = "review-rule-engine-v1"


def _safe_mean(series: pd.Series) -> float:
    values = pd.to_numeric(series, errors="coerce").dropna()
    return round(float(values.mean()), 2) if not values.empty else 0.0


INPUT_DATASET = "googleplay_reviews"
OUTPUT_RELATIVE_PATH = Path("googleplay") / "review_analysis.csv"
INSIGHTS_RELATIVE_PATH = Path("googleplay") / "review_insights.csv"


SENTIMENT_NEGATIVE = {
    "pessimo",
    "pesima",
    "horrivel",
    "ruim",
    "lamentavel",
    "instavel",
    "erro",
    "bug",
    "falha",
    "problema",
    "trava",
    "travando",
    "lento",
    "demora",
    "demorado",
    "desliga",
    "fecha",
    "bloqueou",
    "bloqueado",
    "impossivel",
    "dificil",
    "complicado",
    "frustrante",
    "golpe",
    "hacker",
    "vulneravel",
    "vazamento",
    "nao funciona",
    "nao consigo",
    "nao abre",
    "nao atualiza",
    "nao permite",
    "sem acesso",
    "sem conseguir",
    "ninguem resolve",
}

SENTIMENT_POSITIVE = {
    "excelente",
    "otimo",
    "otima",
    "bom",
    "boa",
    "pratico",
    "pratica",
    "facil",
    "intuitivo",
    "intuitiva",
    "confiavel",
    "rapido",
    "agilidade",
    "eficiencia",
    "perfeito",
    "perfeita",
    "maravilhoso",
    "maravilhosa",
    "recomendo",
    "satisfeito",
    "satisfeita",
    "util",
    "praticidade",
    "ajuda",
    "eficaz",
    "sensacional",
}

STRONG_NEGATIVE_PHRASES = {
    "nao consigo",
    "nao funciona",
    "nao abre",
    "nao atualiza",
    "nao permite",
    "sem acesso",
    "ninguém resolve",
    "ninguem resolve",
    "péssima experiencia",
    "pessima experiencia",
    "falha de seguranca",
    "vazamento de dados",
}

TOPIC_RULES: dict[str, tuple[str, ...]] = {
    "seguranca_privacidade": (
        "seguranca",
        "segurança",
        "vulneravel",
        "vazamento",
        "dados pessoais",
        "golpe",
        "hacker",
    ),
    "manutencao_agendamento": (
        "revisao",
        "revisão",
        "manutencao",
        "manutenção",
        "agendar",
        "agendamento",
        "servico",
        "serviço",
        "oficina",
        "pneu",
    ),
    "acesso_login": (
        "login",
        "logar",
        "senha",
        "entrar",
        "acesso",
        "desloga",
        "deslog",
        "nao entra",
        "não entra",
        "nao consigo entrar",
    ),
    "pagamento_financeiro": (
        "fatura",
        "boleto",
        "pagamento",
        "pagar",
        "pagando",
        "cartao",
        "cartão",
        "debito automatico",
        "débito automático",
        "vencimento",
        "juros",
        "cobranca",
        "cobrança",
    ),
    "multas_condutor": (
        "multa",
        "condutor",
        "indicar condutor",
    ),
    "contrato_assinatura": (
        "contrato",
        "assinatura",
        "parcelas",
        "renovacao",
        "renovação",
        "cancelar",
        "cancelamento",
        "carro alugado",
        "carro de assinatura",
    ),
    "suporte_atendimento": (
        "atendimento",
        "suporte",
        "whatsapp",
        "central",
        "pos venda",
        "pós venda",
        "ninguém",
        "ninguem",
        "chamado",
        "e-mail",
        "email",
    ),
    "notificacoes": (
        "notificacao",
        "notificação",
        "notificacoes",
        "notificações",
        "aviso",
        "avisos",
        "lembrar",
        "lembrete",
    ),
    "telemetria_localizacao": (
        "localizacao",
        "localização",
        "telemetria",
        "rastreamento",
        "tempo real",
        "km",
        "quilometragem",
        "combustivel",
        "combustível",
        "bateria",
    ),
    "entrega_veiculo": (
        "entrega",
        "em transporte",
        "localizacao do carro",
        "localização do carro",
        "retirada",
        "processo do carro",
    ),
    "mobilidade_viagem": (
        "viagem",
        "viajar",
        "rota",
        "planejamento",
        "planejar",
        "estrada",
        "pedagio",
        "pedágio",
    ),
    "beneficios": (
        "beneficio",
        "benefício",
        "beneficios",
        "benefícios",
        "desconto",
        "clube",
        "parceiro",
    ),
    "performance_estabilidade": (
        "trava",
        "travando",
        "bug",
        "erro",
        "lento",
        "demora",
        "demorado",
        "instavel",
        "instável",
        "fecha",
        "desliga",
        "carregando",
        "atualizacao",
        "atualização",
        "atualizar",
        "fora de servico",
        "fora de serviço",
    ),
}

PAIN_RULES: dict[str, tuple[str, ...]] = {
    "erro_funcional": (
        "nao funciona",
        "não funciona",
        "nao consigo",
        "não consigo",
        "nao permite",
        "não permite",
        "nao abre",
        "não abre",
        "nao consigo fazer",
        "não consigo fazer",
        "fica travado",
        "travado",
    ),
    "performance_estabilidade": (
        "trava",
        "travando",
        "lento",
        "demora",
        "instavel",
        "instável",
        "desliga",
        "fecha",
        "carregando",
        "atualizacao",
        "atualização",
        "fora de servico",
        "fora de serviço",
    ),
    "usabilidade": (
        "complicado",
        "dificil",
        "difícil",
        "facil de",
        "fácil de",
        "intuitivo",
        "não entendo",
        "nao entendo",
        "poucas informacoes",
        "poucas informações",
    ),
    "dados_desatualizados": (
        "nao atualiza",
        "não atualiza",
        "nao aparece",
        "não aparece",
        "informacao desatualizada",
        "informação desatualizada",
        "informacoes desatualizadas",
        "informações desatualizadas",
        "nao localiza meu contrato",
        "não localiza meu contrato",
    ),
    "atendimento": (
        "atendimento",
        "suporte",
        "whatsapp",
        "central",
        "pos venda",
        "pós venda",
        "ninguem resolve",
        "ninguém resolve",
    ),
    "funcionalidade_ausente": (
        "falta",
        "faltam",
        "poderia ter",
        "deveria ter",
        "seria bom ter",
        "mais opcoes",
        "mais opções",
        "nao tem opcao",
        "não tem opção",
        "sem a possibilidade",
    ),
    "notificacao_excessiva": (
        "muitas notificacoes",
        "muitas notificações",
        "notificacoes demais",
        "notificações demais",
    ),
    "seguranca_privacidade": (
        "seguranca",
        "segurança",
        "vazamento",
        "dados pessoais",
        "golpe",
        "hacker",
        "vulneravel",
        "vulnerável",
    ),
}


OPPORTUNITY_MAP = {
    "manutencao_agendamento": ("proactive_care", "Agendar revisão"),
    "telemetria_localizacao": ("zero_surpresa", "Ver status do carro e uso"),
    "pagamento_financeiro": ("zero_surpresa", "Revisar pagamentos e vencimentos"),
    "contrato_assinatura": ("zero_surpresa", "Ver contrato e próximos eventos"),
    "mobilidade_viagem": ("mobility_planner", "Planejar mobilidade"),
    "beneficios": ("beneficio_contextual", "Ver benefício relevante"),
    "suporte_atendimento": (
        "support_prevention",
        "Resolver necessidade antes do contato",
    ),
    "notificacoes": ("notification_control", "Ajustar notificações"),
    "acesso_login": ("app_reliability", "Resolver acesso ao app"),
    "performance_estabilidade": ("app_reliability", "Corrigir experiência do app"),
    "seguranca_privacidade": ("security_trust", "Reforçar segurança e confiança"),
    "multas_condutor": ("zero_surpresa", "Resolver multas e condutor"),
    "entrega_veiculo": ("zero_surpresa", "Acompanhar entrega do veículo"),
}

PRODUCT_AREA_MAP = {
    "manutencao_agendamento": "manutencao",
    "acesso_login": "conta_acesso",
    "pagamento_financeiro": "financeiro",
    "multas_condutor": "multas",
    "contrato_assinatura": "contrato",
    "suporte_atendimento": "suporte",
    "beneficios": "beneficios",
    "notificacoes": "notificacoes",
    "telemetria_localizacao": "telemetria",
    "entrega_veiculo": "entrega",
    "mobilidade_viagem": "mobilidade",
    "performance_estabilidade": "app",
    "seguranca_privacidade": "seguranca",
    "funcionalidade_usabilidade": "experiencia_app",
}

JOURNEY_MAP = {
    "manutencao_agendamento": "manutencao",
    "acesso_login": "acesso",
    "pagamento_financeiro": "financeiro",
    "multas_condutor": "multas",
    "contrato_assinatura": "contrato",
    "suporte_atendimento": "suporte",
    "beneficios": "beneficios",
    "notificacoes": "relacionamento",
    "telemetria_localizacao": "uso_do_carro",
    "entrega_veiculo": "entrega",
    "mobilidade_viagem": "viagem",
    "performance_estabilidade": "uso_do_app",
    "seguranca_privacidade": "confianca",
    "funcionalidade_usabilidade": "uso_do_app",
    "geral": "uso_do_app",
}


def normalize_text(text: Any) -> str:
    if text is None or (isinstance(text, float) and pd.isna(text)):
        return ""
    value = str(text).strip().lower()
    value = unicodedata.normalize("NFKD", value)
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    value = re.sub(r"[^a-z0-9\s]", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def _hits(text: str, phrases: set[str] | tuple[str, ...]) -> list[str]:
    return [phrase for phrase in phrases if normalize_text(phrase) in text]


def classify_sentiment(text: str, rating: Any) -> tuple[str, int, float, list[str]]:
    normalized = normalize_text(text)
    neg = _hits(normalized, {normalize_text(x) for x in SENTIMENT_NEGATIVE})
    pos = _hits(normalized, {normalize_text(x) for x in SENTIMENT_POSITIVE})
    strong = _hits(normalized, {normalize_text(x) for x in STRONG_NEGATIVE_PHRASES})

    score = len(pos) - len(neg) + (3 * len(strong))
    rating_value = float(rating) if pd.notna(rating) else 3.0
    score += 1 if rating_value >= 4 else -1 if rating_value <= 2 else 0

    if strong:
        score = -max(2, abs(score))
    elif rating_value <= 2 and neg:
        score = min(score, -1)

    if score <= -2:
        label = "negativo"
    elif score >= 2:
        label = "positivo"
    elif rating_value <= 2 and not pos:
        label = "negativo"
    elif rating_value >= 4 and not neg:
        label = "positivo"
    else:
        label = "neutro"

    evidence = [f"neg:{x}" for x in neg] + [f"pos:{x}" for x in pos]
    evidence += [f"forte_neg:{x}" for x in strong]
    evidence.append(f"rating:{int(rating_value)}")
    confidence = min(0.98, 0.50 + min(abs(score), 4) * 0.10 + (0.08 if strong else 0.0))
    return label, int(score), round(confidence, 2), evidence


def classify_by_rules(
    text: str, rules: dict[str, tuple[str, ...]]
) -> tuple[str, list[str]]:
    normalized = normalize_text(text)
    scores: dict[str, int] = {}
    evidence: dict[str, list[str]] = {}
    for label, phrases in rules.items():
        hits = _hits(normalized, {normalize_text(x) for x in phrases})
        if hits:
            scores[label] = len(hits)
            evidence[label] = hits

    if not scores:
        return "geral", []
    best_score = max(scores.values())
    candidates = [label for label, score in scores.items() if score == best_score]
    best = candidates[0]
    flat = [f"{best}:{x}" for x in evidence[best]]
    return best, flat


def classify_voice_signal(text: str, sentiment: str) -> str:
    normalized = normalize_text(text)
    suggestion_markers = (
        "falta",
        "poderia",
        "deveria",
        "seria bom",
        "melhorar",
        "gostaria",
    )
    if any(marker in normalized for marker in suggestion_markers):
        return "sugestao"
    if sentiment == "negativo":
        return "dor"
    if sentiment == "positivo":
        return "elogio"
    return "neutro"


def classify_pain(text: str, topic: str, sentiment: str) -> tuple[str, list[str]]:
    pain, evidence = classify_by_rules(text, PAIN_RULES)
    if pain != "geral":
        return pain, evidence
    if sentiment == "negativo":
        if topic in {"performance_estabilidade", "acesso_login"}:
            return "disponibilidade", [f"topic:{topic}"]
        return "friccao_na_jornada", [f"topic:{topic}"]
    return "nenhuma", []


def classify_urgency(text: str, rating: Any, sentiment: str, pain: str) -> str:
    normalized = normalize_text(text)
    high_markers = (
        "impossivel",
        "nao consigo",
        "nao funciona",
        "nao abre",
        "vulneravel",
        "vazamento",
        "golpe",
        "bloqueado",
        "ninguém resolve",
        "ninguem resolve",
        "meses",
        "semanas",
    )
    rating_value = float(rating) if pd.notna(rating) else 3.0
    if sentiment == "negativo" and (
        pain == "seguranca_privacidade" or any(x in normalized for x in high_markers)
    ):
        return "alta"
    if rating_value <= 2 or sentiment == "negativo":
        return "media"
    return "baixa"


def analyze_reviews(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()
    output: list[dict[str, Any]] = []

    for _, row in result.iterrows():
        text = "" if pd.isna(row.get("review_text")) else str(row.get("review_text"))
        sentiment, sentiment_score, sentiment_conf, sentiment_evidence = (
            classify_sentiment(text, row.get("rating"))
        )
        topic, topic_evidence = classify_by_rules(text, TOPIC_RULES)
        if topic == "geral" and sentiment == "negativo":
            topic = "funcionalidade_usabilidade"
            topic_evidence = ["fallback:sentimento_negativo"]

        journey = JOURNEY_MAP.get(topic, "uso_do_app")
        pain, pain_evidence = classify_pain(text, topic, sentiment)
        urgency = classify_urgency(text, row.get("rating"), sentiment, pain)
        opportunity, action = OPPORTUNITY_MAP.get(topic, ("none", "nenhuma"))
        if sentiment != "negativo" and topic == "geral":
            opportunity, action = "none", "nenhuma"

        product_area = PRODUCT_AREA_MAP.get(topic, "experiencia_app")
        voice_signal = classify_voice_signal(text, sentiment)

        all_evidence = sentiment_evidence + topic_evidence + pain_evidence
        confidence = max(0.5, min(0.98, sentiment_conf))
        if topic != "geral":
            confidence = min(0.98, confidence + 0.08)
        if pain not in {"nenhuma", "geral"}:
            confidence = min(0.98, confidence + 0.04)

        output.append(
            {
                "review_id": row.get("review_id"),
                "rating": row.get("rating"),
                "review_text": text,
                "review_date": row.get("review_date"),
                "app_version": row.get("app_version"),
                "thumbs_up_count": row.get("thumbs_up_count"),
                "reply_content": row.get("reply_content"),
                "data_origin": row.get("data_origin", "GOOGLE_PLAY"),
                "normalized_text": normalize_text(text),
                "sentiment": sentiment,
                "sentiment_score": sentiment_score,
                "sentiment_confidence": sentiment_conf,
                "voice_signal": voice_signal,
                "topic": topic,
                "journey_moment": journey,
                "pain_category": pain,
                "urgency": urgency,
                "product_area": product_area,
                "context_opportunity": opportunity,
                "recommended_action": action,
                "confidence": round(confidence, 2),
                "matched_signals": " | ".join(dict.fromkeys(all_evidence)),
                "analysis_method": PIPELINE_VERSION,
            }
        )

    analyzed = pd.DataFrame(output)
    for column in ANALYSIS_COLUMNS:
        if column not in analyzed.columns:
            analyzed[column] = None
    return analyzed[ANALYSIS_COLUMNS]


def build_insights(analyzed: pd.DataFrame) -> pd.DataFrame:
    dimensions = [
        "sentiment",
        "topic",
        "journey_moment",
        "pain_category",
        "context_opportunity",
    ]
    rows: list[dict[str, Any]] = []
    total = len(analyzed)

    for dimension in dimensions:
        for label, group in analyzed.groupby(dimension, dropna=False):
            label = str(label)
            count = len(group)
            negative = int(group["sentiment"].eq("negativo").sum())
            high_urgency = int(group["urgency"].eq("alta").sum())
            rows.append(
                {
                    "dimension": dimension,
                    "label": label,
                    "review_count": count,
                    "share_pct": round(count / max(total, 1) * 100, 1),
                    "negative_count": negative,
                    "negative_rate_pct": round(negative / max(count, 1) * 100, 1),
                    "high_urgency_count": high_urgency,
                    "average_rating": _safe_mean(group["rating"]),
                    "actionable_count": int(
                        group["recommended_action"].ne("nenhuma").sum()
                    ),
                }
            )

    return pd.DataFrame(rows).sort_values(
        ["dimension", "negative_count", "review_count"], ascending=[True, False, False]
    )


def run_pipeline(
    *, input_path: Path | None = None, output_path: Path | None = None
) -> tuple[Path, Path, pd.DataFrame]:
    if input_path is None:
        df = load_dataset(INPUT_DATASET).copy()
    else:
        df = pd.read_csv(input_path)

    analyzed = analyze_reviews(df)
    insights = build_insights(analyzed)

    output_path = output_path or DATA_DIR / OUTPUT_RELATIVE_PATH
    insights_path = DATA_DIR / INSIGHTS_RELATIVE_PATH
    output_path.parent.mkdir(parents=True, exist_ok=True)
    insights_path.parent.mkdir(parents=True, exist_ok=True)

    analyzed.to_csv(output_path, index=False)
    insights.to_csv(insights_path, index=False)
    return output_path, insights_path, analyzed


if __name__ == "__main__":
    review_path, insights_path, analyzed = run_pipeline()
    print(f"Reviews analisadas: {len(analyzed)}")
    print(f"Saída: {review_path}")
    print(f"Insights: {insights_path}")
