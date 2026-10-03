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
- `/voice-of-customer` — camada consolidada de Voz do Cliente (Google Play + Reclame AQUI).
- `/reclame-aqui?source=reclameaqui` — visão filtrada para Reclame AQUI.

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
GET /api/reclameaqui/summary
GET /api/reclameaqui
GET /api/reclameaqui/{complaint_id}
GET /api/customer-voice/summary
GET /api/customer-voice
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


## Reclame AQUI

A camada de Reclame AQUI segue o mesmo desenho da camada de Google Play:

```text
Reclamações públicas
        ↓
normalização
        ↓
sentimento / sinal
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
data/reclameaqui/reclameaqui_complaints.csv
data/reclameaqui/complaint_analysis.csv
data/reclameaqui/complaint_insights.csv
data/reclameaqui/reclameaqui_snapshot.csv
```

O snapshot incluído no repositório foi construído a partir de páginas públicas pesquisadas em 02/10/2026. O Reclame AQUI pode usar listagem dinâmica e proteção contra automação; por isso a pipeline mantém `source_url`, `collection_method` e `data_origin`, e oferece um helper de refresh que aceita um snapshot CSV/JSON normalizado.

Para executar a análise:

```bash
uv run localiza reclameaqui
```

A camada consolidada usa as duas fontes:

```text
Google Play + Reclame AQUI
          ↓
     Customer Voice
          ↓
     Context Engine
```

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

## Páginas do projeto

O projeto mantém duas frentes complementares:

### Páginas de dados e análise

- `/` — dashboard e exploração dos dados do protótipo;
- `/voice-of-customer` — análise das reviews do Google Play;
- `/prototype` — demonstração do fluxo conceitual do Context Engine;

### Página de interface

- `/localiza-app` — reconstrução conceitual da interface do Localiza Assinatura/Meoo, baseada em referências públicas, preservando a identidade visual do produto e demonstrando a evolução para uma experiência contextual.

A página de interface não substitui as páginas de dados. Ela complementa a camada analítica com a demonstração visual da experiência proposta.

## Execução

Como o ponto de entrada da aplicação fica dentro do pacote `app`, a API é iniciada por:

```bash
uv run localiza run --reload
```

ou, diretamente:

```bash
uv run uvicorn app.main:app --reload
```

## Ingestão das fontes de voz do cliente

### Reclame AQUI

A CLI coleta a listagem pública paginada da Localiza Meoo usando o endpoint público utilizado pelo site e continua até encontrar uma página vazia (ou até o limite informado):

```bash
uv run localiza reclameaqui
```

Limitar a quantidade de páginas durante testes:

```bash
uv run localiza reclameaqui --pages 20
```

O coletor usa até 10 registros por página, deduplica por `complaint_id` e grava:

- `data/reclameaqui/reclameaqui_complaints.csv`
- `data/reclameaqui/reclameaqui_snapshot.csv`
- `data/reclameaqui/complaint_analysis.csv`
- `data/reclameaqui/complaint_insights.csv`

O endpoint público utilizado pelo coletor não é a RA Data Hub oficial. Para integração corporativa oficial, o Reclame AQUI oferece a RA Data Hub/RA API com autenticação. O coletor deste projeto é destinado à pesquisa pública do hackathon e pode exigir atualização caso a infraestrutura pública do site mude.

### Apple App Store

A CLI coleta o feed público de avaliações da Apple nas 10 páginas públicas disponíveis para o storefront configurado:

```bash
uv run localiza appstore
```

Por padrão usa o storefront `br`. Também é possível informar outro país:

```bash
uv run localiza appstore --country br --pages 10
```

O feed RSS público da Apple é limitado a aproximadamente 10 páginas, cerca de 500 reviews mais recentes por storefront. Portanto, ele não representa todo o histórico existente da App Store. Para recuperar o histórico completo de reviews do próprio app, a Apple disponibiliza a App Store Connect API, que requer acesso/autenticação da conta que publica o app.

O preview de 4 registros só deve ser usado explicitamente:

```bash
uv run localiza appstore --preview
```

A execução normal não cai silenciosamente para o preview; se o feed ao vivo falhar, o comando retorna erro para deixar claro que os dados reais não foram coletados.

## Coleta do Reclame AQUI

A ingestão do Reclame AQUI percorre a paginação pública do BFF e salva um checkpoint a cada página para evitar perda de dados em caso de bloqueio temporário. O cliente utiliza intervalo maior entre requisições, jitter e backoff exponencial para respostas HTTP 403/429.

```bash
uv run localiza reclameaqui
```

Em caso de interrupção, retome do último checkpoint com:

```bash
uv run localiza reclameaqui --resume
```

Para testes curtos, é possível limitar o número de páginas:

```bash
uv run localiza reclameaqui --pages 20
```
