# RAG do Assistente Contextual

O Assistente Contextual agora usa um RAG obrigatório antes de qualquer resposta.

## Fluxo

```text
cliente envia mensagem
        ↓
customer_id obrigatório
        ↓
resolve contrato
        ↓
resolve vehicle_id
        ↓
resolve tipo/modelo/categoria do carro
        ↓
filtra datasets pelo cliente + veículo
        ↓
recupera registros relevantes para a pergunta
        ↓
monta contexto RAG
        ↓
LLM local (Ollama) recebe o contexto
        ↓
tool Python quando uma regra/cálculo é necessário
        ↓
resposta
```

## Regra principal

O RAG nunca faz busca solta em todos os clientes.

Primeiro ele valida `customer_id`, encontra o contrato mais recente e descobre o
`vehicle_id` do cliente. A recuperação detalhada então fica restrita ao cliente e
ao veículo associado ao contrato.

O tipo do carro também entra como metadado de relevância:

- `category`
- `make`
- `model`
- `version`
- `mobility_archetype`

## Fontes usadas

- `clients.csv`
- `contracts.csv`
- `vehicles.csv`
- `telemetry.csv`
- `maintenance.csv`
- `trips.csv`
- `context_events.csv`
- `recommendations.csv`
- `app_events.csv`

## Por que não usar embeddings agora?

Os dados do protótipo são fortemente estruturados. Para perguntas de cliente,
`customer_id` e `vehicle_id` são filtros muito mais confiáveis que uma busca
semântica que pode misturar registros de pessoas diferentes.

A implementação atual é, portanto, um **RAG metadata-first**:

1. filtro estrutural por identidade do cliente;
2. filtro estrutural por veículo;
3. relevância lexical dentro desse universo;
4. contexto recuperado enviado ao LLM.

Quando o volume crescer, pode-se adicionar embeddings sem alterar a interface
`CustomerRAG.retrieve()`.

## Endpoint de debug

```http
GET /api/assistant/retrieval?customer_id=CUST0001&q=Quanto%20ainda%20posso%20rodar
```

Ele permite visualizar exatamente o que foi recuperado antes do LLM responder.

## Tools continuam separadas

O RAG fornece contexto factual. As tools Python continuam responsáveis por
cálculos e regras operacionais, como:

- uso de KM;
- preparação de viagem;
- manutenção;
- contrato;
- benefícios.

Isso evita transformar o LLM em fonte de verdade para cálculos.

## Modelo local

O projeto agora é preparado para Ollama por padrão:

```env
AI_PROVIDER=ollama
OLLAMA_BASE_URL=http://127.0.0.1:11434/v1
LOCALIZA_ASSISTANT_MODEL=qwen2.5:3b-instruct-q4_K_M
```

O projeto continua aceitando `AI_PROVIDER=openai`, caso seja necessário trocar
apenas o provedor sem alterar o RAG ou as tools.
