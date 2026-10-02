# Hackathon Localiza — RUPTURA 2026

Protótipo de dados para o Case 2 — **Do atendimento ao hábito**.

## Executar

Com `uv`:

```bash
uv sync
uv run localiza run --reload
```

Ou diretamente com Uvicorn:

```bash
uv run uvicorn main:app --reload
```

Abra `http://127.0.0.1:8000`.

## Páginas

- `/` — dashboard/explorador de dados.
- `/prototype` — espaço das telas conceituais do protótipo.
- `/voice-of-customer` — análise da Voz do Cliente a partir das reviews do Google Play.

## API

A API segue a organização em `app/api/routes`, inspirada na separação utilizada no BrandPulse.

```text
GET /api/health
GET /api/summary
GET /api/charts
GET /api/datasets
GET /api/datasets/{name}
GET /api/customers
GET /api/customers/{customer_id}/360
GET /api/context-engine/{customer_id}
GET /api/metadata/{name}
GET /api/reviews
GET /api/reviews/summary
GET /api/reviews/{review_id}
GET /api/reviews/analysis-summary
GET /api/reviews/analysis
GET /api/reviews/insights
```

## Google Play Reviews

As reviews do aplicativo `com.localiza.meoo.app` ficam em:

```text
data/googleplay/google_play_reviews.csv
```

A pipeline transforma as reviews em uma camada analítica:

```text
Google Play Reviews
        ↓
normalização
        ↓
sentimento
        ↓
tipo de voz
        ↓
tema
        ↓
momento da jornada
        ↓
pain point
        ↓
urgência
        ↓
oportunidade contextual
        ↓
ação recomendada
        ↓
insights
```

Os artefatos ficam em:

```text
data/googleplay/review_analysis.csv
data/googleplay/review_insights.csv
```

Para executar a análise:

```bash
uv run localiza review
```

Para coletar novamente as reviews:

```bash
uv run localiza ingest
```

A classificação é determinística e explicável. Os dados da review são públicos; as categorias de sentimento, tema, jornada, oportunidade e ação são inferências da pipeline do protótipo.

## Estrutura

```text
app/
├── api/
│   └── routes/
│       ├── analytics.py
│       ├── context.py
│       ├── customers.py
│       ├── datasets.py
│       ├── health.py
│       ├── metadata.py
│       ├── pages.py
│       ├── review_analysis.py
│       └── reviews.py
├── core/
├── ingest/
├── services/
├── static/
└── templates/
    ├── dashboard/
    └── prototype/

main.py
```

`main.py` apenas cria a aplicação, configura middleware/static e registra os routers. As rotas cuidam da camada HTTP, `app/services` concentra regras de negócio e `app/core/data.py` centraliza o acesso aos datasets.

A descrição detalhada está em `docs/ARCHITECTURE.md`.

## Testes

```bash
PYTHONPATH=. pytest -q
```

A suíte atual valida ingestão/análise das reviews, endpoints de reviews e a página de Voz do Cliente.
