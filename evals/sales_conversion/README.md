# Tozi — Sales Conversion Diagnostics Eval

LLM-as-a-Judge eval adaptado do framework `deep-eval-max` do iFood (`hits-eval-export`) pra mercado imobiliário Tozi.

## O que faz

Dado o transcript de uma conversa entre os agentes IA da Tozi (Clara/Júlia/Bruna/Letícia) e um cliente, o LLM judge analisa em 8 dimensões:

| Dimensão | O que captura |
|---|---|
| **interest_level** | Quão engajado o cliente esteve durante a conversa |
| **objections** | Resistências comerciais (cliente **não quer** avançar) |
| **operational_blockers** | Impedimentos externos (cliente **quer mas não pode**) |
| **partner_questions** | Perguntas do cliente e qualidade das respostas |
| **agent_failures** | Falhas conversacionais por agente persona |
| **handoff_quality** | Avaliação de handoff Clara → especialista → humano |
| **funnel_stage + sentiment + intent + loss_trigger + observation** | Resumos diagnósticos |

Output é JSON estruturado — pronto pra agregar em SQL.

## Arquivos

```
tozi/evals/sales_conversion/
  manifest.yaml   # Metadata (id, target_agents, funnel_stages)
  prompt.md       # System prompt completo do LLM judge
  schema.json     # Schema de output (builda Pydantic em runtime)
  README.md       # Este arquivo
  runner.py       # Runner standalone (não exige o framework iFood completo)
  examples/       # (futuro) exemplos de transcripts pra calibrar o judge
```

## Origem e adaptação

- **Origem:** `hits-eval-export` do iFood (`/eval/{manifest.yaml, prompt.md, schema.json}`)
- **Framework original:** `deep-eval-max` (interno iFood, com Streamlit UI + SQLite + litellm proxy)
- **Adaptações pra Tozi:**
  - Taxonomias específicas do mercado imobiliário (PRICE_TOO_HIGH, NEGATIVE_CREDIT_DENIED, GUARANTEE_TYPES, etc)
  - Campo `intent_detected` (LOCACAO, VENDA, SUPORTE_*) — não existe no original
  - Campo `agent_persona` em cada falha (CLARA/JULIA/BRUNA/LETICIA) — multi-agente
  - Campo `handoff_quality` dedicado — original do iFood é single-agent
  - Funnel stages adaptados ao funil Tozi (TRIAGE/QUALIFICATION/PROPERTY_DISCUSSION/VISIT_NEGOTIATION/PRE_DEAL)

## Como rodar (versão MVP standalone)

```bash
cd tozi/evals/sales_conversion
python -m venv .venv && .venv\Scripts\activate
pip install anthropic httpx pydantic python-dotenv
# .env com ANTHROPIC_API_KEY=...

# 1. Exportar transcripts do SPX (próximo: script tooling)
python runner.py export-from-spx --conversation-id 18 > transcript.txt

# 2. Rodar eval em uma conversa
python runner.py eval --transcript transcript.txt

# 3. Rodar em lote (CSV com coluna formatted_conversation)
python runner.py eval-batch --csv conversas.csv --out results.jsonl
```

## Input mínimo por conversa

| Campo | Tipo | Descrição |
|---|---|---|
| `formatted_conversation` | str | Transcript completo, alternando turnos. Ver formato abaixo. |

Opcionais (filtros analíticos):
- `conversation_id` (SPX), `contact_id`, `start_date`, `agent_chain` (ex: "Clara → Bruna")

### Formato do transcript

```
[Clara]: Oi, tudo bem? Como posso te ajudar?
[Cliente]: Quero alugar uma casa em Sinop
[Clara]: Ótimo! Em qual região?
[Cliente]: Centro
[Bruna]: Oi! Sou a Bruna da locação. Pra centro a gente tem várias opções...
```

A IA reconhece os turnos por `[Nome]:` e categoriza falhas por `agent_persona`.

## Aplicações downstream

1. **Dashboard de objections** — qual é a #1 objection na Tozi? `GROUP BY objections[].category`
2. **Funnel drop analysis** — onde o lead some? `GROUP BY funnel_stage`
3. **Quality scorecard por agente** — Júlia vs Bruna em `agent_failures`
4. **Handoff timing analysis** — quantos % de handoffs são `TOO_EARLY` ou `TOO_LATE`?
5. **Calibração de prompt** — falha recorrente sinaliza prompt que precisa ajuste

## Próximos passos

- [ ] `runner.py` standalone (chama Claude com schema → Pydantic → JSONL)
- [ ] Script `export-from-spx` que puxa conversas resolvidas e formata
- [ ] Dashboard Streamlit local (5 cards: objections top 5, blockers top 5, funnel, persona scorecard, handoff timing)
- [ ] Cron semanal exportando + rodando eval em todas conversas resolvidas da semana
- [ ] Persistir em Supabase ou SQLite com schema versionado pra análise temporal
- [ ] Loop de melhoria: top falhas → update prompt → re-eval

## Por que isso importa

O Captain registra `Captain::AssistantLog` (response, handoff, tool_use, error) — bom pra debug. Mas não diz **por que** lead não converteu. Eval LLM-as-a-Judge enche essa lacuna com taxonomia estável, queryável e comparável conversa-a-conversa, agente-a-agente, semana-a-semana.

A partir do momento que tiver volume (>100 conversas/semana), as agregações ficam estatisticamente significativas e viram base pra decisão: trocar prompt da Júlia, criar nova tool, ajustar tom da Clara, etc.
