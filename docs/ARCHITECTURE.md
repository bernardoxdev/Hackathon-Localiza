# Arquitetura — Hackathon Localiza

A organização da API segue como referência a estrutura usada no BrandPulse:

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
```

## Responsabilidade das rotas

### `app/api/routes/pages.py`

Endpoints de apresentação das páginas HTML do protótipo:

- `GET /`
- `GET /prototype`
- `GET /voice-of-customer`

### `app/api/routes/health.py`

Endpoint operacional:

- `GET /api/health`

### `app/api/routes/datasets.py`

Exploração genérica dos datasets:

- `GET /api/datasets`
- `GET /api/datasets/{name}`

### `app/api/routes/analytics.py`

Indicadores e dados agregados do dashboard:

- `GET /api/summary`
- `GET /api/charts`

### `app/api/routes/customers.py`

Dados e visão 360 do cliente:

- `GET /api/customers`
- `GET /api/customers/{customer_id}/360`

### `app/api/routes/context.py`

Motor conceitual de contexto:

- `GET /api/context-engine/{customer_id}`

### `app/api/routes/metadata.py`

Metadados e dicionário dos datasets:

- `GET /api/metadata/{name}`

### `app/api/routes/reviews.py`

Acesso às reviews brutas do Google Play:

- `GET /api/reviews`
- `GET /api/reviews/summary`
- `GET /api/reviews/{review_id}`

### `app/api/routes/review_analysis.py`

Acesso às classificações produzidas pela pipeline de voz do cliente:

- `GET /api/reviews/analysis-summary`
- `GET /api/reviews/analysis`
- `GET /api/reviews/insights`

## Fluxo da aplicação

```text
Página / cliente HTTP
        ↓
app/api/routes
        ↓
services
        ↓
core/data
        ↓
CSV / dados do protótipo
```

As rotas cuidam da camada HTTP e não implementam a lógica de classificação ou ingestão. As regras de processamento ficam em `app/services` e a leitura padronizada dos datasets fica em `app/core/data.py`.

A estrutura não introduz banco ou repository apenas por simetria com o BrandPulse. Neste projeto, os dados ainda são consumidos de CSVs; caso a persistência evolua, uma camada de repository pode ser adicionada sem alterar a responsabilidade das rotas.

## Organização das páginas

A aplicação mantém as páginas de dados separadas das páginas de prototipação visual:

```text
app/templates/
├── dashboard/
│   ├── index.html
│   └── voice_of_customer.html
└── prototype/
    ├── index.html
    └── localiza_app.html
```

As rotas de páginas ficam em `app/api/routes/pages.py`. A interface conceitual do Localiza Assinatura é acessada em `/localiza-app`, enquanto `/` continua sendo a área principal de dados e `/voice-of-customer` continua dedicada à análise das reviews.


## Voz do cliente

As fontes públicas de voz do cliente são tratadas separadamente na ingestão e consolidadas pela API `customer_voice`:

```text
Google Play ──────┐
Reclame AQUI ─────┼──→ análise padronizada → Customer Voice → Context Engine
Apple App Store ──┘
```

O App Store usa o feed público de reviews da Apple quando disponível no ambiente de execução. O projeto também mantém um preview público explicitamente marcado para desenvolvimento offline.
