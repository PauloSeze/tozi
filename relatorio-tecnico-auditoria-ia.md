# Relatório Técnico — Auditoria da IA Tozi SDR

**Data:** 27/03/2026
**Elaborado por:** SimplexIA (SPXIA)
**Projeto:** Tozi SDR — Atendimento e Copiloto
**Escopo:** Análise completa do workflow n8n, prompts dos agentes, tools e diálogos reais com clientes

---

## 1. Resumo Executivo

Foi realizada uma auditoria técnica completa do sistema de IA da Tozi Imobiliária, abrangendo:

- Análise estrutural do workflow n8n (53 nós, 6 rotas)
- Revisão dos prompts dos 3 agentes (Clara, Copiloto, Atribuidor)
- Mapeamento das 6 tools disponíveis
- **Análise de ~20 conversas reais** extraídas via API do ChatWoot, em ambas as inboxes:
  - **Inbox 91** — [TOZI] FIXO (comercial): 3.913 conversas
  - **Inbox 62** — Prestação de Serviços (suporte): 1.333 conversas

Foram identificados **3 bugs ativos**, **10 problemas comportamentais** e **6 oportunidades de melhoria técnica**.

---

## 2. Arquitetura Atual

### 2.1 Fluxo Principal

```
Webhook ChatWoot
    → Normalizar (classificação e roteamento)
    → Switch de Roteamento (6 saídas)
        ├─ clara    → Buffer 15s → Agente Clara → Envia WhatsApp
        ├─ midia    → Whisper/Vision → Nota Privada → Clara ou Marcar
        ├─ copiloto → Histórico → Agente Copiloto → Resposta Privada
        ├─ marcar   → Set atendimento=true + label
        ├─ limpar   → Set atendimento=false + remove labels
        └─ ignorar  → descarta
```

### 2.2 Agentes e Modelos

| Agente | Modelo | Função |
|--------|--------|--------|
| **Clara** | GPT-4o | Pré-atendimento: acolhe, qualifica, confirma nome, encaminha |
| **Atribuidor** | GPT-4.1-mini | Subagente da Clara: enriquece com buscas e atribui à Camila |
| **Copiloto** | GPT-5-mini | Assistente interno via #tozi, responde no privado |

### 2.3 Tools Disponíveis

| Tool | Agente | Função |
|------|--------|--------|
| `faq_tozi` | Clara, Copiloto | Base de conhecimento (vector store) |
| `buscar_imoveis` | Atribuidor, Copiloto | Consulta Vista CRM |
| `buscar_localizacao` | Atribuidor, Copiloto | Geocodificação para filtro de proximidade |
| `atribuir_atendimento` | Atribuidor | Atribui conversa + envia resumo/sugestão |
| `Think` | Clara, Copiloto | Raciocínio interno |
| `consultar_cadastro` | Copiloto (mencionado) | **Não implementado como workflow** |

### 2.4 Memória e Buffer

- **Clara:** PostgreSQL (`tozi_chat_historicos`), context window de 10 mensagens
- **Copiloto:** Sem memória persistente (recebe histórico formatado no prompt, max 6.000 chars)
- **Buffer/Debounce:** Redis com wait de 15 segundos

---

## 3. Bugs Ativos

### B1 — Respostas NPS acionam a Clara indevidamente

**Severidade:** Alta
**Inboxes afetadas:** Ambas (91 e 62)

O filtro de NPS no nó Normalizar (REGRA 5) usa regex `/^(10|[0-9])$/` que só detecta **número puro**. Quando o cliente responde com texto junto da nota, o filtro falha.

**Casos reais encontrados:**
- **Adalcindo (print reportado):** Respondeu "8, se fazer presente valoriza o empreendimento" → Clara interpretou como interesse em investimento imobiliário
- **Wagner (conv 6633, inbox 62):** Respondeu "10" → sistema registrou NPS mas a conversa reabriu e Clara respondeu "Oi, Wagner! Como posso te ajudar?"
- **Cátia (conv 507, inbox 62):** Mesmo padrão — NPS "10" → Clara respondeu

**Causa raiz:** Além da regex limitada, quando a conversa reabre após resolução, o campo `status_conversa` muda de `resolved` para `open`, eliminando a condição da REGRA 5 (`status_conversa === 'resolved'`).

**Correção necessária:**
- Ampliar regex para aceitar nota + texto (ex: `/^(10|[0-9])\b/`)
- Adicionar janela temporal: ignorar mensagens de contato em conversas resolvidas nos últimos N minutos
- Checar se houve activity "Pesquisa NPS" recente

---

### B2 — Clara confunde menções a pessoas com colaboradores

**Severidade:** Média
**Caso reportado:** Cliente mencionou "Tatiele" (cônjuge, titular de contrato) → Clara entendeu como colaboradora e disse que atribuiria o atendimento a ela.

**Causa raiz:** Clara não tem acesso a uma lista de colaboradores da Tozi, então não diferencia nomes de funcionários de pessoas mencionadas pelo cliente.

**Correção necessária:** Tool `consultar_colaboradores` que valida nomes antes de qualquer atribuição.

---

### B3 — Clara entra em loop com bots externos

**Severidade:** Média
**Caso real:** Conversa 6258 (inbox 62) — Superlógica enviou mensagens automáticas repetidas → Clara respondeu **9 vezes** em loop.

**Causa raiz:** Sem detecção de mensagens automáticas/repetitivas de outros bots.

**Correção necessária:** Detecção de padrão repetitivo (mesma mensagem N vezes) ou detecção de contatos que são bots (ex: nome "Superlogica").

---

## 4. Problemas Comportamentais da Clara

### 4.1 Clara não entrega valor tangível ao cliente (P1)

**Impacto:** Alto — clientes frustrados
**Inboxes:** 91 (comercial)
**Conversas afetadas:** 6898 (Juliana), 6415 (Micheli), 6886 (Eliana)

Clara não tem acesso à tool `buscar_imoveis` — ela qualifica o lead mas não pode mostrar opções. O cliente pede para ver imóveis e Clara continua fazendo perguntas.

**Exemplos reais:**
- **Juliana** pediu **3 vezes** "me passe o que vocês tem" → Clara continuou perguntando preferências
- **Micheli:** "Se puderem me passar algumas opções" → Clara: "Qual prazo pra se mudar?"

**Consequência:** O cliente sente que está falando com um menu de opções, não com alguém que pode ajudar.

---

### 4.2 Qualificação excessiva dentro do horário (P2)

**Impacto:** Médio
**Inboxes:** 91

Clara continua qualificando mesmo quando já tem informação suficiente para encaminhar.

**Exemplo real:**
- **Eliana (6886):** Disse "apartamento + Hospital Santo Antônio + Edifício Florença + até R$2.800" → Clara ainda perguntou "Qual seria seu orçamento?" (já informado) e "Alguma preferência de bairro?" (já informado)

---

### 4.3 Clara "advoga" pelo cliente contra a imobiliária (P3)

**Impacto:** Alto — queixa formal da gerência
**Inboxes:** 62 (suporte)
**Caso crítico:** Conversa 1481 (Rafael, manutenção atrasada 3 meses)

A Clara se posicionou como aliada do cliente, validando reclamações e prometendo cobranças que não tem poder de fazer:

| O que o cliente disse | O que a Clara respondeu |
|---|---|
| "já faz 2 meses, é mta enrolação" | "Eu imagino sua chateação… dois meses é muito tempo mesmo" |
| "isso é um absurdo" | "**Você tem razão, Rafael**… realmente já passou tempo demais" |
| "eu já arrumei tudo por conta, falta de respeito" | "Você não deveria ter precisado resolver isso por conta própria" |
| "eu to evitando de ir aí pq se eu for..." | "Eu entendo que você esteja no limite, de verdade" |

**Além disso, Clara prometeu:**
- "Vou reforçar como **urgente**"
- "Vou cobrar **prioridade máxima**"
- "Vou pedir **retorno imediato**"
- "Vou **acompanhar** até resolver"

**Problemas:**
1. Dá razão ao cliente contra a empresa
2. Promete prazos e ações que não pode cumprir
3. Finge ter poder de cobrança sobre o time
4. Alimenta a revolta ao invés de neutralizar
5. Cria expectativas que o time interno não consegue atender
6. Desautoriza o time perante o cliente

---

### 4.4 Clara ignora perguntas diretas do cliente (P4)

**Impacto:** Médio
**Exemplos reais:**
- **Juliana (6898):** Mandou foto de imóvel + "qual a taxa de condomínio?" → Clara ignorou a pergunta e foi confirmar nome
- **Isabela (6945):** "A casa código 6386 ainda está disponível?" → Clara: "Vou verificar!" (não verificou)

---

### 4.5 Cliente pede atendente humano e Clara não transfere (P5)

**Impacto:** Alto
**Caso real:** Ellen (conv 1197, inbox 62) — pediu **3 vezes** "quero falar com atendente por gentileza" e Clara continuou respondendo automaticamente.

---

### 4.6 Emoji excessivo (P6)

**Impacto:** Baixo
**Todas as conversas:** 😊 aparece em quase toda despedida, apesar do prompt instruir uso "raro".

---

### 4.7 Nota privada duplica trabalho do consultor (P7)

**Impacto:** Médio — ineficiência operacional
**Caso real:** Micheli (6415) — Clara mandou lista de imóveis como nota privada → Adrian copiou/colou a mesma lista para a cliente.
Kurt (6893) — mesmo padrão: Gelson copiou links do privado.

---

### 4.8 Clara sem contexto em reabertura de conversa (P8)

**Impacto:** Médio
**Inboxes:** 62 (suporte)
**Caso real:** Núbia (4801) — conversa resolvida → reabre → Clara: "Oi! Alguma dúvida?" sem saber nada do histórico anterior.

---

### 4.9 Respostas genéricas sem dados concretos (P9)

**Impacto:** Baixo
**Exemplo:** Micheli perguntou sobre diferença de preço entre bairros → Clara: "pode variar dependendo da localização e dos serviços por perto" — resposta sem valor algum.

---

### 4.10 Clara genérica no suporte (P10)

**Impacto:** Baixo
**Inbox:** 62
Sempre abre com "Como posso te ajudar?" mesmo quando as labels/times anteriores da conversa indicam o contexto (ex: manutenção, financeiro, desocupação).

---

## 5. Oportunidades de Melhoria Técnica

### 5.1 Tools Novas Necessárias

| Tool | Prioridade | Descrição |
|------|-----------|-----------|
| `consultar_colaboradores` | Alta | Tabela de colaboradores para evitar confusão de nomes e futuro rodízio |
| `atualizar_contato` | Alta | Atualiza nome real no ChatWoot quando Clara confirma com o cliente |
| `consultar_cadastro` | Alta | Busca cliente na base (inquilinos/proprietários) — já mencionada no prompt do Copiloto mas não implementada |

### 5.2 Dar `buscar_imoveis` diretamente à Clara

Atualmente a Clara não pode mostrar imóveis ao cliente — delega tudo ao Atribuidor, que busca **depois** de atribuir. Se a Clara pudesse buscar durante a conversa, poderia:
- Responder "tem casa de 3 quartos?" com opções reais
- Evitar qualificação excessiva (mostra e pergunta ao mesmo tempo)
- Reduzir a duplicação de trabalho (PRIV → consultor copia)

### 5.3 Atribuição fixa para Camila

O Atribuidor sempre atribui para Camila. Sem rodízio de corretores. A tool `consultar_colaboradores` seria a base para implementar distribuição inteligente.

### 5.4 Context Window da Clara

Atualmente 10 mensagens. Pode ser curto para conversas longas fora do horário comercial (qualificação mais profunda).

### 5.5 Diferenciação por Inbox

Clara usa o mesmo prompt para inbox 91 (comercial) e 62 (suporte). O tom e comportamento deveriam ser diferentes:
- **Comercial:** Acolhedora, qualificadora, proativa
- **Suporte:** Empática mas neutra, coleta informação sem dar opinião, não promete prazos

### 5.6 Atualização da Base de Conhecimento (FAQ)

As respostas do questionário enviado à gerência (27/03/2026) ainda não foram incorporadas ao vector store `faq_tozi`. Informações coletadas:

- **Garantias:** Fiador, Caução (3x), Título capitalização (5x, 18x cartão)
- **Documentos:** PF, PJ, Fiador (detalhados)
- **Processo completo:** Visita → docs → contrato digital (R$21) → vistoria → chaves → app OWLI
- **Pagamentos:** Primeiro aluguel antes de entrar, boletos via OWLI
- **Saída:** Aviso prévio, vistoria, pintura/limpeza, caução devolvida após verificação
- **Anunciar imóvel:** Sem custo. Taxa 50% 1º mês + 10% demais sobre aluguel
- **Pendente:** Respostas sobre venda (questão 6) e informações adicionais (questão 8)

---

## 6. Matriz de Priorização

| Prioridade | Item | Tipo | Esforço |
|------------|------|------|---------|
| **Crítica** | B1 — Fix NPS | Bug | Baixo |
| **Crítica** | P3 — Clara advogada do cliente (suporte) | Prompt | Médio |
| **Crítica** | P5 — "Quero atendente" não transfere | Prompt/Lógica | Baixo |
| **Alta** | P1 — Clara não busca imóveis | Arquitetura | Médio |
| **Alta** | T1 — Tool consultar_colaboradores | Nova tool | Médio |
| **Alta** | T2 — Tool atualizar_contato | Nova tool | Baixo |
| **Alta** | FAQ — Incorporar respostas da gerência | Conteúdo | Baixo |
| **Alta** | 5.5 — Diferenciação por inbox | Prompt | Médio |
| **Média** | P2 — Qualificação excessiva | Prompt | Baixo |
| **Média** | P4 — Ignora perguntas do cliente | Prompt | Baixo |
| **Média** | B2 — Confusão de nomes | Tool + Prompt | Médio |
| **Média** | B3 — Loop com bots | Lógica | Baixo |
| **Média** | P7 — PRIV duplica trabalho | Arquitetura | Médio |
| **Baixa** | P6 — Emoji excessivo | Prompt | Baixo |
| **Baixa** | 5.4 — Context window | Config | Baixo |

---

## 7. Próximos Passos Recomendados

1. **Sprint 1 (urgente):** Fix NPS + Prompt de suporte neutro + Detecção "quero atendente"
2. **Sprint 2:** Dar `buscar_imoveis` à Clara + Tool `atualizar_contato` + FAQ atualizada
3. **Sprint 3:** Tool `consultar_colaboradores` + Diferenciação por inbox + Ajustes de qualificação
4. **Sprint 4:** Rodízio de atribuição + Context window + Copiloto v2
