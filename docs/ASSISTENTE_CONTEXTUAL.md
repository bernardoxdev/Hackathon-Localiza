# Assistente Contextual

O Assistente Contextual agora usa quatro camadas:

```text
frontend
   ↓
POST /api/assistant/message
   ↓
RAG obrigatório
   ↓
customer_id → contrato → vehicle_id → tipo/modelo do carro
   ↓
contexto recuperado dos datasets
   ↓
LLM local (Ollama)
   ↓
Tools Python quando houver cálculo/regra/ação
   ↓
resposta
```

A regra principal é: **nenhuma resposta é produzida antes de uma recuperação de dados pelo RAG**.

## 1. RAG obrigatório

O código está em `app/services/rag.py`.

O fluxo é: 

1. validar `customer_id`;
2. localizar o contrato do cliente;
3. descobrir o `vehicle_id`;
4. carregar o tipo/categoria, marca, modelo, versão e arquétipo do veículo;
5. filtrar os dados do cliente e do veículo;
6. priorizar registros relacionados à pergunta;
7. montar o contexto que será enviado ao modelo.

Fontes consultadas pelo RAG:

- `clients.csv`;
- `contracts.csv`;
- `vehicles.csv`;
- `telemetry.csv`;
- `maintenance.csv`;
- `trips.csv`;
- `context_events.csv`;
- `recommendations.csv`;
- `app_events.csv`.

A implementação é **metadata-first**: para os dados estruturados do protótipo, o filtro por identidade do cliente e veículo é feito antes da relevância textual. Isso reduz o risco de misturar informações de clientes diferentes.

## 2. Ver o que foi recuperado

Use:

```http
GET /api/assistant/retrieval?customer_id=CUST0001&q=Quanto%20ainda%20posso%20rodar
```

O endpoint retorna os documentos recuperados, score, fonte e metadados.

## 3. Configurar o modelo local

A configuração padrão usa Ollama:

```env
AI_PROVIDER=ollama
OLLAMA_BASE_URL=http://127.0.0.1:11434/v1
OLLAMA_API_KEY=ollama
LOCALIZA_ASSISTANT_MODEL=qwen2.5:3b-instruct-q4_K_M
```

Baixe o modelo no computador:

```bash
ollama pull qwen2.5:3b-instruct-q4_K_M
```

Depois inicie o projeto:

```bash
uv sync
uv run localiza run --reload
```

Também é possível usar OpenAI sem alterar o RAG, definindo `AI_PROVIDER=openai` e `OPENAI_API_KEY`.

## 4. Adicionar uma nova funcionalidade

O ponto principal continua sendo `app/services/assistant.py`.

Crie uma função Python e registre com `@register_tool`:

```python
@register_tool(
    "get_benefits",
    "Consulta benefícios disponíveis para o cliente.",
    parameters={
        "type": "object",
        "properties": {},
        "required": [],
        "additionalProperties": False,
    },
)
def get_benefits(customer_id: str) -> dict[str, Any]:
    return {
        "available": True,
        "items": [],
        "data_origin": "SYNTHETIC",
    }
```

O modelo poderá chamar a função quando a intenção exigir essa consulta. A resposta, porém, já terá passado pelo RAG obrigatório.

## 5. Como controlar o jeito da resposta

No começo de `app/services/assistant.py` existe `RESPONSE_BEHAVIOR`:

```python
RESPONSE_BEHAVIOR = {
    "language": "pt-BR",
    "tone": "natural, próximo e objetivo",
    "max_sentences": 5,
    "use_bullets_when_useful": True,
    "never_invent_customer_data": True,
    "never_invent_actions": True,
    "mention_synthetic_data_when_relevant": True,
}
```

Para regras mais específicas, use `customize_tool_result()` no mesmo arquivo.

## 6. Ações reais

As tools atuais são principalmente de consulta. Para adicionar uma ação real, crie outra tool Python e exija confirmação antes de executar qualquer operação que altere dados.

## 7. Endpoint do chatbot

```http
POST /api/assistant/message
```

Body:

```json
{
  "customer_id": "CUST0001",
  "message": "Quanto ainda posso rodar?",
  "history": []
}
```

A resposta contém, além da mensagem, `tool_calls` e `rag`, permitindo demonstrar quais dados foram recuperados e quais ferramentas foram usadas.

## 8. Capacidades atuais

- `get_customer_context`
- `get_km_status`
- `get_maintenance_status`
- `get_contract_status`
- `get_trip_readiness`
- `get_customer_routine`
- `get_contextual_benefits`
- `get_recent_recommendations`

A lista está disponível em:

```http
GET /api/assistant/capabilities
```
