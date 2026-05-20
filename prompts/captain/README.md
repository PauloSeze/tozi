# Prompts Captain — Tozi Imóveis

Versão dos prompts adaptada para o **Captain do SPX (chatspx)** — runtime nativo dentro do ChatWoot, com gem `ai-agents` e `ruby_llm`. Sucessor dos prompts n8n em `tozi/prompts/`.

**Decisão arquitetural** (2026-05-04/06): toda a parte conversacional roda no Captain, com Clara como Assistant principal e os 3 especialistas como Scenarios (handoff via `Agents::Runner`).

## Mapa

| Arquivo | Vira |
|---|---|
| `clara.md` | `Captain::Assistant` (id 1) — `description` + response_guidelines + guardrails + behavior |
| `julia-vendas.md` | `Captain::Scenario` — title "Vendas", instruction = persona Júlia |
| `bruna-locacao.md` | `Captain::Scenario` — title "Locação", instruction = persona Bruna |
| `leticia-suporte.md` | `Captain::Scenario` — title "Suporte", instruction = persona Letícia |

## Tom comum (não negociável)

- Primeira pessoa do plural: "a gente", "aqui na Tozi" — nunca terceira pessoa
- Acentuação perfeita em todo PT-BR
- Mensagens picadas: máx 3 frases por envio
- Sem formalidade forçada, sem frases feitas
- Uma pergunta por vez
- Sem promessas de prazo, valor ou disponibilidade
- Emoji só se natural (máx 1)

## Modelo

Claude Sonnet 4.5 (configurado no Captain Preferences).

## Como o handoff funciona

1. Cliente manda mensagem → cai na Clara (Assistant principal vinculado à Inbox)
2. Clara conversa, identifica intent
3. Clara chama tool `handoff_to_scenario_{id}_vendas_agent` (ou locacao/suporte) — feito automaticamente pelo Captain
4. O Scenario assume a conversa, agora com a persona Júlia/Bruna/Letícia
5. Especialista qualifica e, quando pronto, chama tool `atribuir_humano` (Captain::CustomTool) que assigna pro Team SPX certo (id 1/2/3/4)

A memória da conversa é preservada entre todos (gem ai-agents cuida disso via `Agents::Runner`).
