# Tozi SDR - Atendimento e Copiloto

**Cliente:** Tozi Imobiliária (Sinop/MT)
**Status:** Em implementação
**Última atualização:** 09/02/2026

## Visão Geral

Sistema de atendimento automatizado para imobiliária com dois agentes principais:

- **Clara** - Pré-atendimento (recepciona, qualifica, atribui)
- **Copiloto** - Assistente interno (ajuda o time sob demanda via `#tozi`)

---

## Arquivos do Projeto

```
projetos/tozi/
├── README.md                              # Este arquivo (visão geral)
├── BACKLOG.md                             # Roadmap de desenvolvimento
├── estado-projeto-tozi-atualizado.md      # Documentação técnica detalhada
├── analise-nodes.md                       # Análise e renomeação dos 53 nodes
├── Tozi SDR - Atendimento e Copiloto.json # Fluxo principal n8n (original)
├── Tozi SDR - RENOMEADO.json              # Fluxo com nodes renomeados
├── Tozi SDR - FINAL.json                  # Fluxo final com sticky notes
├── transform-v2.js                        # Script de renomeação de nodes
├── add-sticky-notes.js                    # Script de adição de sticky notes
│
├── subworkflows/                          # ✅ Fluxos auxiliares (tools)
│   ├── Tozi TOOL - Atribuir Atendimento.json  # ID: PTHEJTw8ZWkgXt7F
│   ├── Tozi TOOL - Buscar imóveis.json        # ID: ZvrUozDnbEzRZfFs
│   └── Tozi TOOL - Buscar Localização.json    # ID: dTUGxaH5AwEDFen0
│
└── prompts/                               # ✅ System prompts extraídos
    ├── prompt-clara.md                    # Pré-atendimento
    ├── prompt-atribuidor.md               # Subagente de enriquecimento
    ├── prompt-copiloto.md                 # Assistente interno
    ├── prompt-humanizador.md              # Formatação WhatsApp
    ├── prompt-vision-imagem.md            # Análise de imagem
    └── tools-descricoes.md                # Descrições das tools
```

---

## Arquitetura

```
WEBHOOK (ChatWoot/SPX)
    │
    ▼
NORMALIZAR ──────────────────────────────────────────────────┐
    │                                                         │
    ├─► clara ────► [Buffer] → [Wait] → AI Agent Clara        │
    │                              ↓                          │
    │                         Atribuidor (subagente)          │
    │                              ↓                          │
    │                         Humanizador → Envia mensagens   │
    │                                                         │
    ├─► midia ────► [Tipo Mídia] → Transcreve/Analisa         │
    │                    ↓                                    │
    │               Formatar → Nota Privada → Rota Final      │
    │                                                         │
    ├─► copiloto ─► [Busca Histórico] → Agente Copiloto       │
    │                    ↓                                    │
    │               Resposta Privada                          │
    │                                                         │
    ├─► marcar ───► HTTP: set atendimento=true                │
    │                                                         │
    ├─► limpar ───► HTTP: set atendimento=false               │
    │                                                         │
    └─► ignorar ──► NOOP                                      │
```

---

## Nodes do Fluxo Principal (53 total)

### Entrada e Roteamento

| Node | Tipo | Função |
|------|------|--------|
| Webhook | webhook | Recebe eventos do ChatWoot |
| If | if | Filtro inicial |
| Normalizar | code | Classifica e padroniza webhook |
| Roteamento | switch | Direciona por `rota` |
| Tipo Mídia | switch | Direciona por `tipo_conteudo` |
| Rota Final | switch | Direciona pós-processamento de mídia |

### Agente Clara (Pré-Atendimento)

| Node | Tipo | Função |
|------|------|--------|
| Buffer Mensagem1 | redis | Agrupa mensagens do cliente |
| Wait 15s1 | wait | Aguarda mais mensagens |
| Busca Buffer1 | redis | Recupera mensagens agrupadas |
| Limpa Buffer1 | redis | Limpa buffer após processar |
| Verifica se tem mais mensagens1 | if | Verifica se há mais mensagens |
| Prepara Contexto1 | set | Prepara input para agente |
| AI Agent | agent | Agente Clara (pré-atendimento) |
| OpenAI Chat Model2 | lmChatOpenAi | LLM da Clara |
| Postgres Chat Memory1 | memoryPostgresChat | Memória persistente |
| faq_tozi | vectorStoreInMemory | Base de conhecimento |
| Think1 | toolThink | Tool de raciocínio |
| Embeddings | embeddingsOpenAi | Embeddings para vector store |

### Atribuidor (Subagente da Clara)

| Node | Tipo | Função |
|------|------|--------|
| Atribuidor | agentTool | Subagente que enriquece e atribui |
| OpenAI Chat Model4 | lmChatOpenAi | LLM do Atribuidor |
| buscar_imoveis | toolWorkflow | Busca imóveis no Vista |
| buscar_localizacao | toolWorkflow | Geocoding de referências |
| atribuir_atendimento | toolWorkflow | Atribui conversa para Camila |

### Humanizador e Saída Clara

| Node | Tipo | Função |
|------|------|--------|
| Basic LLM Chain | chainLlm | Humanizador de respostas |
| OpenAI Chat Model3 | lmChatOpenAi | LLM do Humanizador |
| Structured Output Parser1 | outputParserStructured | Parser de JSON |
| OpenAI Chat Model1 | lmChatOpenAi | LLM do Parser |
| Split Out | splitOut | Separa mensagens do array |
| Loop Over Items | splitInBatches | Itera sobre mensagens |
| Envia Mensagem Inteira1 | httpRequest | Envia mensagem ao ChatWoot |

### Agente Copiloto

| Node | Tipo | Função |
|------|------|--------|
| pega_historico | httpRequest | Busca histórico da conversa |
| Code in JavaScript | code | Formata histórico para prompt |
| Agente Copilot | agent | Agente assistente interno |
| GPT-4o-mini | lmChatOpenAi | LLM do Copiloto |
| buscar_imoveis1 | toolWorkflow | Busca imóveis (Copiloto) |
| buscar_localizacao1 | toolWorkflow | Geocoding (Copiloto) |
| faq_tozi1 | vectorStoreInMemory | Base de conhecimento (Copiloto) |
| Embeddings OpenAI | embeddingsOpenAi | Embeddings (Copiloto) |
| Think | toolThink | Tool de raciocínio (Copiloto) |
| Envia Mensagem Inteira | httpRequest | Envia resposta privada |

### Processamento de Mídia

| Node | Tipo | Função |
|------|------|--------|
| Pega Áudio1 | httpRequest | Download do áudio |
| Transcrever Áudio1 | openAi | Whisper transcrição |
| Analisar Imagem1 | openAi | GPT-4o-mini análise de imagem |
| Formatar Mídia | code | Formata resultado para nota |
| Envia Mensagem Inteira3 | httpRequest | Envia nota privada |
| Code in JavaScript2 | code | Prepara dados pós-mídia |
| Edit Fields | set | Ajusta campos para Clara |

### Controle de Atendimento

| Node | Tipo | Função |
|------|------|--------|
| Marca atendimento | httpRequest | Set atendimento=true |
| Marca atendimento1-4 | httpRequest | Variações do marcador |
| Limpa atendimento | httpRequest | Set atendimento=false |

---

## Subworkflows (Tools)

### Tozi TOOL - Buscar imóveis
**ID:** `ZvrUozDnbEzRZfFs` | **Nodes:** 4

Busca imóveis na API Vista CRM com filtros dinâmicos.

| Input | Output |
|-------|--------|
| `query.filter` (objeto) | `imoveis` (array) |
| `query.advFilter` (objeto) | Cada imóvel com `url` gerada |
| `query.order` (objeto) | |
| `query.paginacao` (objeto) | |

**Exemplo de uso:**
```json
{
  "query": {
    "filter": { "Cidade": "Sinop", "Categoria": "Casa", "ValorLocacao": ["", 2000] },
    "advFilter": {},
    "order": { "Codigo": "desc" },
    "paginacao": { "pagina": 1, "quantidade": 5 }
  }
}
```

### Tozi TOOL - Buscar Localização
**ID:** `dTUGxaH5AwEDFen0` | **Nodes:** 3

Converte nome de local em coordenadas (bounding box de 3km) para filtro no Vista.

| Input | Output |
|-------|--------|
| `local` (string) | `Latitude` (array [min, max]) |
| | `Longitude` (array [min, max]) |

**Exemplo:** `"unifasipe sinop mt"` → ranges de lat/lng para filtrar imóveis próximos.

### Tozi TOOL - Atribuir Atendimento
**ID:** `PTHEJTw8ZWkgXt7F` | **Nodes:** 8

Atribui conversa para Camila (ID: 66) e envia notas privadas com resumo e sugestão.

| Input | Output |
|-------|--------|
| `sender_id` (number) | `output` (string de confirmação) |
| `chat_id` (number) | |
| `resumo` (string, obrigatório) | |
| `sugestao` (string, pode ser vazio) | |

**Fluxo:**
1. Atribui conversa para Camila (`assignee_id: 66`)
2. Envia resumo como nota privada
3. Se houver sugestão, envia como segunda nota
4. Reabre conversa (`status: open`)
5. Retorna confirmação

---

## Integrações

| Sistema | Base URL | Credential |
|---------|----------|------------|
| ChatWoot (SPX) | `https://chat.simplexsolucoes.com.br` | SPX - Bot / SPX - Paulo |
| Vista CRM | `https://toz19328-rest.vistahost.com.br` | Vista - Tozi |
| OpenAI | API | OpenAi account |
| Redis | - | Redis account |
| PostgreSQL | - | (Chat Memory) |

---

## Rotas do Normalizar

| Rota | Condição | Destino |
|------|----------|---------|
| `clara` | Cliente sem atendimento + texto | AI Agent Clara |
| `midia` | Cliente/atendente + mídia processável | Transcrição/Análise → Rota Final |
| `copiloto` | Atendente + privado + `#tozi` | Agente Copiloto |
| `marcar` | Atendente responde publicamente | Set atendimento=true |
| `limpar` | Conversa resolved | Set atendimento=false |
| `ignorar` | Bot, activity, NPS, grupo, etc | Noop |

---

## Horário Comercial

| Dia | Horário |
|-----|---------|
| Seg-Sex | 7:30-11:30 e 13:30-17:30 |
| Sábado | 9:00-11:30 |
| Domingo | Fechado |

---

## Próximos Passos

1. [x] ~~Baixar subworkflows (Tools) do n8n~~
2. [x] ~~Renomear nodes com nomenclatura clara~~
3. [x] ~~Adicionar sticky notes para documentação visual~~
4. [x] ~~Exportar prompts dos agentes para arquivos .md~~
5. [ ] Testar fluxo completo Clara → Atribuidor → Camila

**Ver [BACKLOG.md](./BACKLOG.md) para roadmap completo de desenvolvimento.**

## Roadmap (Resumo)

| Prioridade | Item | Status |
|------------|------|--------|
| 🔥 Alta | Tool: Consultar Cadastro de Clientes | 🔴 |
| 🔥 Alta | Evaluation: Conversas IA ↔ Cliente | 🔴 |
| ⚡ Média | Agente: Follow-up Clientes Ociosos | 🔴 |
| ⚡ Média | Evaluation: Conversas Atendente ↔ Cliente | 🔴 |
| ⚡ Média | Tool: Perguntar Grupo de Gerentes | 🔴 |
| ⚡ Média | Portal: FAQ e Playbooks para Gerentes | 🔴 |
| 📋 Baixa | Copiloto v2 (Observador Automático) | 🔴 |

---

## Documentação Detalhada

Ver [estado-projeto-tozi-atualizado.md](./estado-projeto-tozi-atualizado.md) para:
- Especificação completa do Normalizar
- System prompts dos agentes
- Formato de saída das tools
- **Documentação completa dos 3 subworkflows**
- Decisões de arquitetura
- Referências de expressões n8n
- Lista de credenciais utilizadas
