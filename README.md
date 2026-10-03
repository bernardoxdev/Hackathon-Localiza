# Infraestrutura Docker — Hackathon Localiza

Arquivos de infraestrutura para executar a API FastAPI com Gunicorn e múltiplos workers, PostgreSQL e Redis.

## Instalação

Copie `.env.example` para `.env` e ajuste principalmente `POSTGRES_PASSWORD`.

```bash
cp .env.example .env
```

## Subir os serviços

```bash
docker compose up --build
```

A API roda com **Gunicorn + UvicornWorker**. O número de workers é controlado por:

```env
WEB_CONCURRENCY=2
```

Para aumentar:

```env
WEB_CONCURRENCY=3
```

Depois recrie a API:

```bash
docker compose up -d --build api
```

## Serviços

- API: `http://localhost:8000`
- PostgreSQL: `localhost:5432`
- Redis: `localhost:6379`

Dentro da rede Docker, a API deve usar:

- PostgreSQL: `postgres:5432`
- Redis: `redis:6379`

## Gunicorn

A API usa:

- `app.main:app` como aplicação ASGI
- `uvicorn_worker.UvicornWorker` como worker ASGI
- logs de acesso e erro enviados para stdout/stderr do container
- timeout padrão de 120 segundos
- graceful timeout de 30 segundos
- keep-alive de 5 segundos

## Ollama no host

O `.env.example` usa `host.docker.internal:11434` para permitir que o container da API acesse um Ollama executando no computador host.
