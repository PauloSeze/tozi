# Estado Atual do Projeto Tozi — Atualizado

**Data:** 09/02/2026
**Status:** Em implementação — fluxo principal funcional, ajustes finos em andamento

---

## 1. Arquitetura Geral

```
WEBHOOK SPX (message_created / conversation_status_changed)
    │
    ▼
NORMALIZAR (Code Node v2)
    │
    ├─ rota: "clara" ────────────► AGENTE CLARA (pré-atendimento)
    │                                   │
    │                                   ▼
    │                              ATRIBUIDOR (subagente/tool)
    │                                   │
    │                                   ▼
    │                              Camila (humana) → Time correto
    │
    ├─ rota: "midia" ────────────► SWITCH MÍDIA
    │                                ├─ audio ──► Transcrição → Formatar → Nota Privada
    │                                ├─ imagem ─► Análise → Formatar → Nota Privada
    │                                └─ resto ──► direto (sem processamento)
    │                                   │
    │                                   ▼
    │                              SWITCH ROTA FINAL
    │                                ├─ "clara" → AGENTE CLARA
    │                                └─ "marcar" → MARCAR ATENDIMENTO
    │
    ├─ rota: "copiloto" ────────► BUSCA HISTÓRICO (API SPX)
    │                                   │
    │                                   ▼
    │                              FORMATAR HISTÓRICO (Code Node)
    │                                   │
    │                                   ▼
    │                              AGENTE COPILOTO → Resposta privada
    │
    ├─ rota: "marcar" ──────────► HTTP: set atendimento=true (conversa)
    │
    ├─ rota: "limpar" ──────────► HTTP: set atendimento=false (conversa)
    │
    └─ rota: "ignorar" ─────────► NOOP
```

---

## 2. Normalizar (Code Node v2)

Ponto central de roteamento. Recebe webhook bruto do SPX, classifica e padroniza num objeto limpo.

### Eventos tratados

| Evento | Tratamento |
|--------|-----------|
| `message_created` | Classifica por sender_type, private, content |
| `conversation_status_changed` (resolved) | Rota `limpar` |
| `conversation_status_changed` (outros) | Ignorar |
| Outros eventos | Ignorar |

### Regras de roteamento

| Origem | Condição | Rota | Rota Final |
|--------|----------|------|------------|
| contact | sem atendimento + texto | `clara` | `clara` |
| contact | sem atendimento + mídia processável | `midia` | `clara` |
| copiloto | user privado + `#tozi` | `copiloto` | `copiloto` |
| user público | mensagem pública | `marcar` | `marcar` |
| user público | mídia processável | `midia` | `marcar` |
| resolved | status changed | `limpar` | `limpar` |
| agent_bot, activity, NPS, grupo, vazio | — | `ignorar` | `ignorar` |

### Campos de saída

```javascript
{
  // Roteamento
  rota,                // 'clara' | 'copiloto' | 'midia' | 'marcar' | 'limpar' | 'ignorar'
  rota_final,          // destino pós-processamento de mídia
  motivo_rota,         // descrição legível da decisão

  // Conversa
  conversa_id,
  inbox_id,
  status_conversa,
  labels,
  em_atendimento,      // boolean (lido de conversation.custom_attributes)
  custom_attributes,   // todos os custom_attributes da conversa

  // Contato
  contato_id,
  nome_cliente,
  nome_atendente,

  // Conteúdo
  tipo_conteudo,       // 'texto' | 'audio' | 'imagem' | 'video' | 'documento' | 'localizacao' | 'contato' | 'sticker' | 'sem_conteudo'
  tipo_evento,         // 'mensagem' | 'status_changed'
  texto,               // conteúdo limpo (sem #tozi se copiloto)
  texto_humano,        // representação legível pra agentes
  legenda,             // legenda de mídia (se houver)

  // Mídia
  midia,               // { tipo, url, thumb_url, file_size, file_name, width, height, ... }

  // Metadados
  autor,               // 'cliente' | 'atendente' | 'clara' | 'sistema'
  mensagem_id,
  sender_id,
  privado,
  timestamp,
  evento_original
}
```

### Detecção de autor

| sender_type | message_type | private | autor |
|-------------|-------------|---------|-------|
| Contact | 0 (incoming) | false | `cliente` |
| User | 1 (outgoing) | false | `atendente` |
| User | 1 (outgoing) | true | `interno` |
| agent_bot | 1 (outgoing) | false | `clara` |
| null/system | — | — | `sistema` |

### Decisões importantes sobre o Normalizar

- **`em_atendimento`** lido de `conversation.custom_attributes`, NÃO de contato
- **`contato`** (tipo_conteudo) deve ser mapeado como mídia processável (rota `midia`), não como conteúdo não-processável
- **`#tozi`** é removido do texto quando origem é copiloto
- **Grupos** detectados via `@g.us` no source_id → ignorados
- **NPS survey** (`content_attributes.nps_survey === true`) → ignorado

---

## 3. Agentes

### 3.1 Clara (Pré-Atendimento)

**Papel:** Recepciona cliente, entende demanda, qualifica, confirma nome, chama atribuidor.

**Arquivo:** `prompt-clara-v3.md`

**Comportamento por horário:**
- Dentro do expediente → ágil: coleta básico e atribui
- Fora do expediente → conversador: qualifica mais fundo, monta dossiê rico

**Tools:**
- `faq_tozi` — base de conhecimento (vector store)
- `atribuir_atendimento` — subagente atribuidor (chamado em linguagem natural)

**Memória:** Postgres Chat Memory, sessionId = `conversa_id`

**User prompt:** `{{ $('Normalizar').item.json.texto_humano }}`
(ou `{{ $json.texto_final }}` quando vem da rota mídia processada)

**Contexto no system prompt:**
```
Nome do cliente (WhatsApp): {{ $('Normalizar').item.json.nome_cliente || 'Não identificado' }}
Atribuído à: {{ $('Normalizar').item.json.nome_atendente || 'Ninguém' }}
Resumo prévio: {{ $('Normalizar').item.json.custom_attributes.resumo || 'Sem resumo' }}
```

**Formato de saída:** JSON `{"messages":["msg1","msg2"]}` com schema de output parser. Quando/se Output Parser do n8n der problemas, alternativa é Code Node `parse-resposta.js` pós-agente.

**Humanizador (opcional):** Agente pós-Clara que formata as respostas para WhatsApp, quebra em mensagens curtas e ajusta tom. Separação de responsabilidades — Clara foca em lógica, humanizador foca em formato.

**Princípios:**
- Humano primeiro, vendedor depois
- Uma pergunta por mensagem
- Confirma nome antes de atribuir
- Sem exemplos de mensagens no prompt (guia comportamental)

### 3.2 Atribuidor (Subagente)

**Papel:** Enriquece handoff com buscas, monta resumo/sugestão, atribui pra Camila.

**Arquivo:** `prompt-atribuidor-v4.md`

**Fluxo:**
1. Recebe contexto da Clara em linguagem natural
2. Busca imóveis/localização se aplicável
3. Chama `atribuir_atendimento` com resumo + sugestão
4. Retorna confirmação pra Clara

**Tools:**
- `buscar_localizacao` — coordenadas via Google Geocoding
- `buscar_imoveis` — API Vista (já retorna URL do site)
- `consultar_cadastro` — busca cliente (endpoint Vista ainda não definido)
- `atribuir_atendimento` — tool unificada (envia privadas + atribui)

**Tool `atribuir_atendimento` input:**
```json
{
  "sender_id": 123,
  "chat_id": 123,
  "resumo": "texto obrigatório",
  "sugestao": "texto ou string vazia"
}
```

**Sem memória** — executa uma vez e termina. Compartilha contexto com Clara via memória da conversa.

### 3.3 Copiloto (Assistente sob demanda)

**Papel:** Assiste o time nos bastidores. Acionado via `#tozi` em mensagem privada.

**Arquivo:** `prompt-copiloto-v3.md`

**Fluxo:**
1. Webhook detecta: user + private + `#tozi`
2. HTTP Request busca histórico: `GET /api/v1/accounts/6/conversations/{conversa_id}/messages`
3. Code Node `formatar-historico.js` formata mensagens + pergunta atual
4. Agente recebe `prompt_copiloto` (histórico + pergunta)
5. Resposta enviada automaticamente como mensagem privada

**User prompt:** `{{ $('Formatar Histórico').item.json.prompt_copiloto }}`

**Tools:**
- `buscar_imoveis` — API Vista
- `buscar_localizacao` — coordenadas
- `consultar_cadastro` — busca cliente
- `faq_tozi` — base de conhecimento

**Output:** Resposta vai como mensagem privada (não é tool, é HTTP Request pós-agente).

**Sem memória** — cada chamada é independente. Contexto vem do histórico via API.

**Princípios:**
- Direto e acionável
- Não faz perguntas ao atendente
- Se pode buscar, busca em vez de sugerir
- Invisível pro cliente

---

## 4. Processamento de Mídia

### Filosofia

Resultado do processamento é **persistido no ChatWoot** como nota privada. Isso garante que qualquer agente ou humano que consulte o histórico veja a transcrição/descrição — não depende de qual agente processou.

### Mapeamento por tipo

| Tipo | Processamento | Nota Privada | Destino |
|------|--------------|-------------|---------|
| texto | Nenhum | Não | Clara/Marcar direto |
| audio | Transcrição | Sim | Clara/Marcar |
| imagem | Análise de imagem | Sim | Clara/Marcar |
| imagem + legenda | Análise + legenda | Sim | Clara/Marcar |
| localizacao | Nenhum (futuro: geocode) | Não | Clara/Marcar direto |
| contato | Nenhum | Não | Clara/Marcar direto |
| video | Nenhum (futuro) | Não | Clara/Marcar direto |
| documento | Nenhum (futuro) | Não | Clara/Marcar direto |
| sticker | Nenhum | Não | Clara/Marcar direto |

### Code Nodes de mídia

**`formatar-midia-v2.js`** — Roda após processamento (transcrição/análise). Produz:
- `mensagem` → body da nota privada (com 📎 e formatação pra humanos)
- `texto_final` → substitui `texto_humano` pro agente

**Nota privada (HTTP Request):**
```json
{
  "content": "{{ $json.mensagem }}",
  "message_type": "outgoing",
  "private": true,
  "content_type": "text"
}
```
URL: `https://chat.simplexsolucoes.com.br/api/v1/accounts/6/conversations/{{ $json.conversa_id }}/messages`

### Switches

**Switch 1 — Roteamento Principal** (campo: `rota`):
| Saída | Rota | Destino |
|-------|------|---------|
| 0 | `clara` | Agente Clara direto |
| 1 | `copiloto` | Busca histórico → Copiloto |
| 2 | `midia` | Switch Mídia |
| 3 | `marcar` | HTTP set atendimento=true |
| 4 | `limpar` | HTTP set atendimento=false |
| fallback | `ignorar` | Noop |

**Switch 2 — Tipo Mídia** (campo: `tipo_conteudo`):
| Saída | Tipo | Processamento |
|-------|------|--------------|
| 0 | `audio` | Transcrição → Formatar → Nota Privada → Switch Rota Final |
| 1 | `imagem` | Análise → Formatar → Nota Privada → Switch Rota Final |
| fallback | resto | Switch Rota Final direto |

**Switch 3 — Rota Final** (campo: `rota_final`):
| Saída | Rota Final | Conecta em |
|-------|-----------|-----------|
| 0 | `clara` | Agente Clara |
| 1 | `marcar` | Marcar Atendimento |

---

## 5. Formatar Histórico (Copiloto)

**Arquivo:** `formatar-historico.js`

Formata mensagens da API SPX para o copiloto. Filtra últimas 30 mensagens relevantes.

**Formato de saída:**
```
[Cliente]: Quero alugar uma casa no centro
[Clara]: Oi! Casa no centro de Sinop, certo?
[Cliente]: [Imagem] Essa região aqui
[Atendente]: Vou verificar disponibilidade
[Interno] (privado): nota interna do atendente

---
Pergunta de Camila: quais imóveis tem nessa região?
```

**Campos de saída:**
- `historico` — string formatada com todas as mensagens
- `prompt_copiloto` — histórico + pergunta atual (pronto pro user prompt)
- `total_mensagens` — contagem

---

## 6. APIs e Integrações

### SPX (ChatWoot)
- **Base:** `https://chat.simplexsolucoes.com.br`
- **Account ID:** 6
- **Credential:** httpHeaderAuth "SPX - Bot" (ID: `IPAsWeAlLuob4Lsy`)

**Endpoints:**
| Endpoint | Uso |
|----------|-----|
| `GET /api/v1/accounts/6/conversations/{id}/messages` | Histórico (copiloto) |
| `POST /api/v1/accounts/6/conversations/{id}/messages` | Enviar mensagem/nota privada |
| `POST /api/v1/accounts/6/conversations/{id}/assignments` | Atribuir agente |
| `PATCH /api/v1/accounts/6/conversations/{id}/custom_attributes` | Atualizar atributos |

**Observação:** `private: true` deve ser **boolean**, não string. Usar `specifyBody: "json"` no n8n.

### Vista (Imóveis)
- **Base:** `https://toz19328-rest.vistahost.com.br/`
- **Credential:** httpQueryAuth "Vista - Tozi" (ID: `PYxEk4SyoSN8RT4h`)

**Endpoint:** `GET /imoveis/listar?pesquisa={json}&showtotal=1`

**Campos retornados:** Codigo, Referencia, Dormitorios, Bairro, Cidade, TipoEndereco, Endereco, Numero, ValorLocacao, Latitude, Longitude, TituloSite, url

**Estrutura do pesquisa:**
```json
{
  "fields": ["Codigo", "Dormitorios", "Bairro", "Endereco", "ValorLocacao", "url"],
  "filter": {},
  "advFilter": {},
  "order": {"Codigo": "desc"},
  "paginacao": {"pagina": 1, "quantidade": 5}
}
```

**Exemplos de filtro:**
- Status aluguel: `["like", "%alug%"]`
- Faixa de valor: `["", 2000]` (até 2000) | `[1000, ""]` (mínimo 1000)
- OR entre campos: `{"Or": {"Campo1": "valor", "Or": {"Campo2": "valor"}}}`

### Google Geocoding
- Tool `buscar_localizacao`
- Sempre adicionar "sinop mt" ao input
- Retorna ranges de latitude/longitude para filtro no Vista

---

## 7. Horário Comercial Tozi

| Dia | Horário |
|-----|---------|
| Seg-Sex | 7:30-11:30 e 13:30-17:30 |
| Sábado | 9:00-11:30 |
| Domingo | Fechado |

---

## 8. Times no SPX

| Time | ID |
|------|-----|
| Corretor de Vendas | 49 |
| Consultor de Locação | 50 |
| Anunciar Imóvel - Venda | 51 |
| Anunciar Imóvel - Locação | 52 |
| Manutenção de Imóvel Locado | 53 |
| Aviso de Desocupação e Vistoria | 54 |
| Renovação de Contrato de Locação | 55 |
| Financeiro | 56 |
| Prestadores de Serviços | 57 |
| Desenvolvedores | 58 |

---

## 9. Decisões Consolidadas

1. **Clara confirma nome** antes de atribuir (nome do WhatsApp pode ser apelido)
2. **Atribuidor é subagente** — Clara chama em linguagem natural, ele enriquece e atribui
3. **Tool `atribuir_atendimento` unificada** — faz resumo + sugestão + atribuição numa chamada só
4. **`sugestao` sempre presente no schema** — manda `""` quando não tem, evita erro de validação
5. **`gerar_links` removida** — `buscar_imoveis` já retorna `url` do site
6. **Copiloto sob demanda** — só responde com `#tozi`, sem observação automática
7. **Copiloto sem memória** — contexto vem do histórico via API + formatador
8. **Sem exemplos de mensagens nos prompts** — comportamento guia, não scripts (engessa o agente)
9. **`em_atendimento` na conversa** — movido de contact-level para conversation-level custom_attributes
10. **Atribuidor sem memória própria** — executa uma vez e termina, não precisa de Postgres Chat Memory
11. **Nota privada como fonte de verdade de mídia** — transcrições/descrições persistidas no ChatWoot
12. **Output Parser removido da Clara** — parse manual via Code Node ou humanizador pós-agente
13. **Humanizador opcional** — agente separado pós-Clara para formatação WhatsApp (separa lógica de formato)

---

## 10. Referências de Expressões n8n

```javascript
// Dados do Normalizar
$('Normalizar').item.json.conversa_id
$('Normalizar').item.json.nome_cliente
$('Normalizar').item.json.nome_atendente
$('Normalizar').item.json.custom_attributes.resumo
$('Normalizar').item.json.texto_humano
$('Normalizar').item.json.tipo_conteudo
$('Normalizar').item.json.midia.url
$('Normalizar').item.json.rota_final

// Session key (Postgres Chat Memory)
{{ 'tozi.chat.memory.' + $('Normalizar').item.json.conversa_id }}

// URLs de API
https://chat.simplexsolucoes.com.br/api/v1/accounts/6/conversations/{{ $('Normalizar').item.json.conversa_id }}/messages

// User prompt Copiloto
{{ $('Formatar Histórico').item.json.prompt_copiloto }}
```

---

## 11. Subworkflows (Tools) — Documentação Completa

### 11.1 Tozi TOOL - Buscar imóveis

**ID:** `ZvrUozDnbEzRZfFs`
**Nodes:** 4
**Status:** Ativo

#### Propósito
Busca imóveis na API Vista CRM com filtros dinâmicos passados pelo agente. Retorna lista de imóveis com URLs do site geradas automaticamente.

#### Schema de Input
```json
{
  "query": {
    "filter": {
      "Cidade": "Sinop",
      "Categoria": "Casa",
      "Status": ["like", "%alug%"],
      "ValorLocacao": ["", 2000]
    },
    "advFilter": {},
    "order": { "Codigo": "desc" },
    "paginacao": { "pagina": 1, "quantidade": 5 }
  }
}
```

#### Campos Retornados pela API Vista
- Codigo, Referencia, ImoCodigo, ImoReferenciaExterna
- Finalidade, TipoImovel, Dormitorios
- Bairro, Cidade, UF, TipoEndereco, Endereco, Numero
- ValorLocacao, Latitude, Longitude
- TituloSite, ExibirNoSite

#### Schema de Output
```json
{
  "imoveis": [
    {
      "Codigo": "9561",
      "Bairro": "Jardim Ouro",
      "Cidade": "Sinop",
      "ValorLocacao": "2000",
      "url": "https://www.toziimoveis.com.br/casa-jardim-ouro-sinop,9561"
    }
  ]
}
```

#### Nodes

| # | Node | Tipo | Função |
|---|------|------|--------|
| 1 | When Executed by Another Workflow | executeWorkflowTrigger | Entrada com schema de query |
| 2 | Edit Fields | set | Extrai fields, filter, advFilter, order, paginacao |
| 3 | Vista - imoveis/listar | httpRequest | Chama API Vista com pesquisa JSON |
| 4 | Edit Fields1 | set | Transforma resposta, gera URLs do site |

#### Credenciais
- **Vista - Tozi** (httpQueryAuth, ID: `PYxEk4SyoSN8RT4h`)

#### Lógica de Geração de URL
```javascript
const slug = (s) => String(s||'')
  .normalize('NFD').replace(/[\u0300-\u036f]/g,'')
  .toLowerCase().replace(/[^a-z0-9]+/g,'-')
  .replace(/(^-|-$)/g,'');

const url = `https://www.toziimoveis.com.br/${slug(titulo)}-${slug(cidade)},${codigo}`;
```

---

### 11.2 Tozi TOOL - Buscar Localização

**ID:** `dTUGxaH5AwEDFen0`
**Nodes:** 3
**Status:** Ativo

#### Propósito
Converte nome de local (referência, bairro, ponto de interesse) em bounding box de coordenadas para filtrar imóveis próximos no Vista.

#### Schema de Input
```json
{
  "local": "unifasipe sinop mt"
}
```

#### Schema de Output
```json
{
  "Latitude": ["-11.885", "-11.831"],
  "Longitude": ["-55.537", "-55.483"]
}
```

O output pode ser usado diretamente no `advFilter` da busca de imóveis:
```javascript
advFilter: {
  Latitude: resultado.Latitude,
  Longitude: resultado.Longitude
}
```

#### Nodes

| # | Node | Tipo | Função |
|---|------|------|--------|
| 1 | When Executed by Another Workflow | executeWorkflowTrigger | Entrada com local string |
| 2 | HTTP Request32 | httpRequest | Chama Google Geocoding API |
| 3 | Code in JavaScript | code | Calcula bounding box 3km |

#### Credenciais
- **Google Maps API Key:** `AIzaSyATs4g6Hs1eM_6aPpqc7VJfOtdM4BJuGoc` (hardcoded)

#### Lógica de Bounding Box
```javascript
const radiusKm = 3;
const radiusMeters = radiusKm * 1000;
const degPerMeterLat = 1 / 111320;
const latRad = lat0 * Math.PI / 180;
const deltaLat = radiusMeters * degPerMeterLat;
const degPerMeterLng = 1 / (111320 * Math.cos(latRad));
const deltaLng = radiusMeters * degPerMeterLng;

// Retorna ranges como strings ordenadas para o Vista
return {
  Latitude: [latMin.toString(), latMax.toString()],
  Longitude: [lngMin.toString(), lngMax.toString()]
};
```

---

### 11.3 Tozi TOOL - Atribuir Atendimento

**ID:** `PTHEJTw8ZWkgXt7F`
**Nodes:** 8
**Status:** Ativo

#### Propósito
Atribui conversa para Camila (corretora, ID: 66), envia notas privadas com resumo e sugestão de imóveis, e reabre a conversa.

#### Schema de Input
```json
{
  "sender_id": 10685,
  "chat_id": 2159,
  "resumo": "📋 Resumo do pré-atendimento\n\nCliente: Paulo Seze\nDemanda: Locação\nDetalhes: Procura casa em Sinop, orçamento até R$ 2.000.",
  "sugestao": "🔍 Imóveis encontrados\n\n5 casas para alugar em Sinop até R$ 2.000:\n• Cód. 9561 — Casa no Jardim Ouro, R$ 2.000/mês — https://www.toziimoveis.com.br/imovel/9561"
}
```

#### Schema de Output
```json
{
  "output": "Atendimento atribuido com sucesso!"
}
```

Ou em caso de erro:
```json
{
  "output": "Houve um erro inesperado."
}
```

#### Nodes

| # | Node | Tipo | Função |
|---|------|------|--------|
| 1 | When Executed by Another Workflow | executeWorkflowTrigger | Entrada com sender_id, chat_id, resumo, sugestao |
| 2 | HTTP Request | httpRequest | POST /assignments (assignee_id: 66) |
| 3 | Envia Mensagem Inteira | httpRequest | POST /messages (resumo, private: true) |
| 4 | If | if | Verifica se sugestao não está vazia |
| 5 | Envia Mensagem Inteira1 | httpRequest | POST /messages (sugestao, private: true) |
| 6 | HTTP Request6 | httpRequest | POST /toggle_status (status: open) |
| 7 | Edit Fields1 | set | Retorna "Atendimento atribuido com sucesso!" |
| 8 | Edit Fields | set | Retorna "Houve um erro inesperado." |

#### Fluxo Visual
```
Trigger → Atribui Camila → Envia Resumo → [Se tem sugestão?]
                                              ├─ Sim → Envia Sugestão → Reabre → Sucesso
                                              └─ Não → Reabre → Sucesso

              (qualquer erro) ──────────────────────────────────► Erro
```

#### Credenciais
- **SPX - Bot** (httpHeaderAuth, ID: `IPAsWeAlLuob4Lsy`) — envio de mensagens
- **SPX - Paulo** (httpHeaderAuth, ID: `4aXAiLt3AYjoyFrC`) — toggle_status

#### API Calls

**1. Atribuir conversa:**
```
POST /api/v1/accounts/6/conversations/{chat_id}/assignments
Headers: api_access_token: 5yDXBtQR5ZLvdyiBecXsDc3t
Body: { "assignee_id": "66" }
```

**2. Enviar nota privada:**
```
POST /api/v1/accounts/6/conversations/{chat_id}/messages
Headers: api_access_token (SPX - Bot)
Body: {
  "content": "{resumo ou sugestao}",
  "message_type": "outgoing",
  "private": true,
  "content_type": "text"
}
```

**3. Reabrir conversa:**
```
POST /api/v1/accounts/6/conversations/{chat_id}/toggle_status
Headers: api_access_token (SPX - Paulo)
Body: { "status": "open" }
```

---

## 12. Arquivos do Projeto

### Scripts de Transformação

| Arquivo | Função |
|---------|--------|
| `transform-v2.js` | Renomeia nodes sem alterar posições |
| `add-sticky-notes.js` | Adiciona sticky notes de documentação |

### Documentação

| Arquivo | Descrição |
|---------|-----------|
| `README.md` | Visão geral e estrutura técnica do fluxo n8n |
| `estado-projeto-tozi-atualizado.md` | Este arquivo - especificação detalhada |

### Fluxos n8n

| Arquivo | ID | Status |
|---------|-----|--------|
| `Tozi SDR - Atendimento e Copiloto.json` | `lEytGA2yzQq606IA` | Principal (original) |
| `Tozi SDR - RENOMEADO.json` | — | Principal (nodes renomeados) |
| `Tozi SDR - FINAL.json` | — | Principal (com sticky notes) |
| `subworkflows/Tozi TOOL - Buscar imóveis.json` | `ZvrUozDnbEzRZfFs` | ✅ Subworkflow |
| `subworkflows/Tozi TOOL - Buscar Localização.json` | `dTUGxaH5AwEDFen0` | ✅ Subworkflow |
| `subworkflows/Tozi TOOL - Atribuir Atendimento.json` | `PTHEJTw8ZWkgXt7F` | ✅ Subworkflow |

### Code Nodes (embutidos no JSON)

| Node | Versão | Descrição |
|------|--------|-----------|
| `Normalizar` | v2 | Roteamento principal |
| `Code in JavaScript` | v1 | Formatar histórico (Copiloto) |
| `Formatar Mídia` | v2 | Formatador pós-processamento |
| `Code in JavaScript2` | v1 | Prepara dados pós-mídia |

### Prompts (extraídos para `prompts/`)

| Arquivo | Agente | Descrição |
|---------|--------|-----------|
| `prompt-clara.md` | AI Agent | Pré-atendimento, qualificação, atribuição |
| `prompt-atribuidor.md` | agentTool | Enriquecimento e atribuição para Camila |
| `prompt-copiloto.md` | AI Agent | Assistente interno via #tozi |
| `prompt-humanizador.md` | chainLlm | Formatação para WhatsApp |
| `prompt-vision-imagem.md` | OpenAI Vision | Análise de imagens |
| `tools-descricoes.md` | — | Descrições de todas as tools |

### Arquivos Legados (referência)

| Arquivo | Versão | Descrição |
|---------|--------|-----------|
| `normalizar-v2.js` | v2 | Code Node principal de roteamento |
| `normalizar-v2.md` | v2 | Especificação completa do Normalizar |
| `prompt-clara-v3.md` | v3 | System prompt da Clara (sem output parser) |
| `prompt-atribuidor-v4.md` | v4 | System prompt do Atribuidor |
| `prompt-copiloto-v3.md` | v3 | System prompt do Copiloto |
| `prompt-humanizador.md` | v1 | System prompt do Humanizador (opcional) |
| `formatar-historico.js` | v1 | Formatador de histórico para Copiloto |
| `formatar-midia-v2.js` | v2 | Formatador pós-processamento de mídia |
| `parse-resposta.js` | v1 | Parser de output da Clara (alternativa ao humanizador) |
| `tools-completo-v2.md` | v2 | Descrições de todas as tools |

---

## 12.1 Nodes do Fluxo Principal (53 total)

```
 1. Webhook                    webhook              Entrada
 2. If                         if                   Filtro inicial
 3. Normalizar                 code                 Roteamento principal
 4. Roteamento                 switch               Switch por rota
 5. Tipo Mídia                 switch               Switch por tipo_conteudo
 6. Rota Final                 switch               Switch pós-mídia

 7. Buffer Mensagem1           redis                Agrupa mensagens cliente
 8. Wait 15s1                  wait                 Aguarda mais mensagens
 9. Busca Buffer1              redis                Recupera buffer
10. Limpa Buffer1              redis                Limpa buffer
11. Verifica se tem mais...    if                   Verifica buffer
12. Prepara Contexto1          set                  Prepara input Clara

13. AI Agent                   agent                Clara (pré-atendimento)
14. OpenAI Chat Model2         lmChatOpenAi         LLM Clara
15. Postgres Chat Memory1      memoryPostgresChat   Memória Clara
16. faq_tozi                   vectorStoreInMemory  Base conhecimento
17. Embeddings                 embeddingsOpenAi     Embeddings FAQ
18. Think1                     toolThink            Tool raciocínio

19. Atribuidor                 agentTool            Subagente Clara
20. OpenAI Chat Model4         lmChatOpenAi         LLM Atribuidor
21. buscar_imoveis             toolWorkflow         Tool Vista
22. buscar_localizacao         toolWorkflow         Tool Geocoding
23. atribuir_atendimento       toolWorkflow         Tool atribuição

24. Basic LLM Chain            chainLlm             Humanizador
25. OpenAI Chat Model3         lmChatOpenAi         LLM Humanizador
26. Structured Output Parser1  outputParserStruct.  Parser JSON
27. OpenAI Chat Model1         lmChatOpenAi         LLM Parser
28. Split Out                  splitOut             Separa mensagens
29. Loop Over Items            splitInBatches       Loop envio
30. Envia Mensagem Inteira1    httpRequest          Envia msg Clara

31. pega_historico             httpRequest          GET histórico
32. Code in JavaScript         code                 Formata histórico
33. Agente Copilot             agent                Copiloto
34. GPT-4o-mini                lmChatOpenAi         LLM Copiloto
35. buscar_imoveis1            toolWorkflow         Tool Vista (Cop.)
36. buscar_localizacao1        toolWorkflow         Tool Geo (Cop.)
37. faq_tozi1                  vectorStoreInMemory  FAQ (Cop.)
38. Embeddings OpenAI          embeddingsOpenAi     Embeddings (Cop.)
39. Think                      toolThink            Raciocínio (Cop.)
40. Envia Mensagem Inteira     httpRequest          Envia resp. privada

41. Pega Áudio1                httpRequest          Download áudio
42. Transcrever Áudio1         openAi               Whisper
43. Analisar Imagem1           openAi               GPT-4o-mini visão
44. Formatar Mídia             code                 Formata resultado
45. Envia Mensagem Inteira3    httpRequest          Nota privada mídia
46. Code in JavaScript2        code                 Prepara pós-mídia
47. Edit Fields                set                  Ajusta campos

48. Marca atendimento          httpRequest          Set true (atend.)
49. Marca atendimento1         httpRequest          Set true (variante)
50. Marca atendimento2         httpRequest          Set true (variante)
51. Marca atendimento3         httpRequest          Set false (após limpa)
52. Marca atendimento4         httpRequest          Set true (variante)
53. Limpa atendimento          httpRequest          Set false (resolved)
```

---

## 12.2 Credenciais Utilizadas

| Credencial | Tipo | ID | Uso |
|------------|------|-----|-----|
| SPX - Bot | httpHeaderAuth | `IPAsWeAlLuob4Lsy` | Envio de mensagens |
| SPX - Paulo | httpHeaderAuth | `4aXAiLt3AYjoyFrC` | Custom attributes, toggle_status |
| OpenAi account | openAiApi | `QJAqRQc73R6XEx3L` | LLMs e Whisper |
| Redis account | redis | `HaUfB6DdzQLeSl8y` | Buffer de mensagens |
| Vista - Tozi | httpQueryAuth | `PYxEk4SyoSN8RT4h` | API imóveis |
| Google Maps | (hardcoded) | — | Geocoding (Buscar Localização) |

---

## 13. Pendências / Próximos Passos

### Concluídos

1. ~~**Baixar subworkflows**~~ — ✅ Todos os 3 subworkflows documentados
2. ~~**Renomear nodes**~~ — ✅ 42 nodes renomeados com nomenclatura clara
3. ~~**Sticky notes**~~ — ✅ 7 sticky notes adicionados para documentação visual
4. ~~**Exportar prompts**~~ — ✅ 6 arquivos em `prompts/` (Clara, Atribuidor, Copiloto, Humanizador, Vision, Tools)

### Pendentes

5. **Tool `consultar_cadastro`** — endpoint Vista para clientes ainda não definido
6. **Copiloto v2 (Observador)** — avaliação automática de todas as mensagens, incluindo respostas da Clara. Estrutura preparada no Normalizar com campo `autor`
7. **Processamento futuro de mídia** — localização (geocode reverso), vídeo (transcrição), documento (extração de texto)
8. **Notificações do Copiloto v2** — sugestões proativas, correções, alertas ao gestor

### Em teste / ajuste fino

9. **Testar fluxo completo** — Clara → Atribuidor → Camila (handoff)
10. **Humanizador vs Parse Resposta** — decidir abordagem final para formatação de saída da Clara
11. **Validar campo `nome_atendente`** no Normalizar — se sempre vem preenchido quando há assignee

### Decisões futuras (Copiloto v2)

O Normalizar já está preparado para uma segunda linha paralela onde o Copiloto recebe tudo e avalia silenciosamente:

```
Linha 1 — Clara (pré-atendimento): gatilho restrito, só clientes sem atendimento
Linha 2 — Copiloto Observador: recebe tudo, avalia, decide se age

Possíveis ações do Copiloto v2:
- Sugerir correção em mensagem do atendente
- Notificar gestor sobre situação crítica
- Avaliar qualidade das respostas da Clara
- Detectar oportunidades comerciais perdidas
- Acompanhar progresso/fechamentos
```

---

## 14. Princípios do Projeto

1. **Humano primeiro, vendedor depois** — rapport antes de qualificar
2. **Uma pergunta por vez** — qualificação progressiva
3. **Contexto é rei** — nunca fazer cliente repetir informação
4. **Dossiê, não formulário** — tools usadas ativamente para enriquecer, não coleta passiva
5. **Copiloto sob demanda** — sugestões só quando solicitadas
6. **Direto e acionável** — informação pronta, não sugestões vagas
7. **Sem scripts nos prompts** — comportamento guia, exemplos enrijecem o agente
8. **ChatWoot como memória compartilhada** — notas privadas são a fonte de verdade entre agentes
