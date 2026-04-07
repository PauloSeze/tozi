# CLAUDE.md — Tozi Agent: Especificação de Migração n8n → Python

Este documento é a fonte única de verdade para a migração do sistema de atendimento da Tozi Imobiliária de n8n para Python. Leia completamente antes de escrever qualquer código.

---

## Contexto do Projeto

**Empresa:** Tozi Imobiliária, Sinop/MT, Brasil  
**Canal:** WhatsApp, integrado via SPX (instância self-hosted do ChatWoot)  
**Objetivo:** Substituir workflows n8n por um servidor Python (FastAPI + Anthropic SDK) que faz exatamente o mesmo trabalho, com controle total do código

**O que existe hoje funcionando em produção (n8n):**
- Clara: agente de pré-atendimento que conversa com clientes no WhatsApp
- Copiloto: assistente interno acionado por atendentes via `#tozi` em nota privada
- Pipeline de mídia: transcreve áudio (Whisper) e descreve imagens (GPT Vision)
- Buffer/debounce: agrupa mensagens rápidas do cliente antes de chamar a Clara
- Humanizador: quebra resposta longa em 1-2 mensagens curtas para WhatsApp
- Controle de atendimento: flags e labels que indicam se humano assumiu a conversa

**O que NÃO muda:**
- SPX (ChatWoot) como plataforma de atendimento
- API do Vista para busca de imóveis
- API do Google Maps para geocoding
- Prompts da Clara e do Copiloto (migrar fielmente do n8n)
- Lógica de negócio (mesmas regras de roteamento)

---

## Infraestrutura e Credenciais

### SPX (ChatWoot self-hosted)
```
Base URL:   https://chat.simplexsolucoes.com.br
Account ID: 6
Inbox prod: [TOZI] FIXO  (ID: 91)
```

**Endpoints usados:**
```
POST   /api/v1/accounts/6/conversations/{id}/messages         → enviar mensagem
PATCH  /api/v1/accounts/6/conversations/{id}                  → atualizar custom_attributes
POST   /api/v1/accounts/6/conversations/{id}/assignments      → atribuir agente
GET    /api/v1/accounts/6/conversations/{id}/messages         → buscar histórico
POST   /api/v1/accounts/6/contacts/{id}/labels                → atualizar labels
```

**Autenticação:** Header `api_access_token: {SPX_BOT_TOKEN}`  
`Content-Type: application/json` obrigatório em todos os POSTs

**IDs fixos:**
```
Camila (agente humana): 66
Time Locação:           50
Time Vendas:            49
Time Financeiro:        56
Time Manutenção:        53
```

### Vista API (imóveis)
```
Base URL: https://toz19328-rest.vistahost.com.br
Auth:     query param ?key={VISTA_API_KEY}
Endpoint: GET /imoveis/listar?pesquisa={json}&showtotal=1
```

**Estrutura do parâmetro `pesquisa` (sempre os 4 campos):**
```json
{
  "fields": ["Codigo", "Categoria", "Status", "Dormitorios", "Cidade",
             "Endereco", "Bairro", "ValorLocacao", "ValorVenda",
             "Latitude", "Longitude", "TituloSite"],
  "filter": {},
  "advFilter": {},
  "order": {"Codigo": "desc"},
  "paginacao": {"pagina": 1, "quantidade": 5}
}
```

**Filtros comuns:**
```json
"Status": ["like", "%alug%"]          // imóveis para alugar
"ValorLocacao": ["", 2000]            // até R$2000
"ValorLocacao": [1000, ""]            // mínimo R$1000
"Categoria": "Casa"                   // Casa | Apartamento | Terreno | Kitnet
"Bairro": "Nome do Bairro"
"Latitude": ["-11.896", "-11.806"]    // vem do buscar_localizacao
"Longitude": ["-55.583", "-55.491"]
```

**URL de imóvel:** `https://www.tozi.com.br/imovel/{Codigo}`

### Google Maps Geocoding
```
URL: https://maps.googleapis.com/maps/api/geocode/json
Params: address={local}&key={GOOGLE_MAPS_KEY}
```

Sempre adicionar "sinop mt" ao endereço. Raio de busca: 3km.

**Cálculo do bbox a partir das coordenadas:**
```python
radius_km = 3
delta_lat = (radius_km * 1000) / 111320
delta_lng = delta_lat / cos(radians(lat))
filter = {
    "Latitude":  [str(lat - delta_lat), str(lat + delta_lat)],
    "Longitude": [str(lng - delta_lng), str(lng + delta_lng)]
}
```

---

## Estrutura Real dos Webhooks do SPX

Os webhooks chegam de dois formatos distintos. Identifique pelo campo `event`.

### Formato A — `message_created`

```python
body = {
    "event": "message_created",
    "message_type": "incoming" | "outgoing",
    "private": True | False,
    "content": "texto da mensagem",
    "attachments": [],          # lista, pode ser vazia
    "source_id": "wamid...",    # ID da mensagem no WhatsApp
    "id": 592904,               # ID da mensagem no SPX

    "sender": {
        # Para CONTATO (cliente): NÃO tem campo "type"
        # Detectar por: "identifier" ou "phone_number" presentes
        "identifier": "556696350491@s.whatsapp.net",
        "phone_number": "+5566996350491",
        "name": "Paulo Seze",
        "id": 10685,
        "custom_attributes": {
            "atendimento": True   # ← ATENÇÃO: pode estar aqui (nível contato)
        }
        # Para USUÁRIO (atendente): tem "type": "user"
        # Para AGENT_BOT:           tem "type": "agent_bot"
    },

    "conversation": {
        "id": 2159,
        "inbox_id": 91,
        "status": "open",
        "labels": ["atendimento"],          # ← flag de atendimento MAIS CONFIÁVEL
        "custom_attributes": {
            "atendimento": True,            # pode estar aqui OU ausente
            "resumo": "texto do resumo"
        },
        "contact_inbox": {
            "source_id": "5566996350491",   # número WhatsApp (checar @g.us para grupos)
        },
        "meta": {
            "sender": {"name": "Paulo Seze", "id": 10685},
            "assignee": {"name": "Camila", "id": 66}   # null se não atribuído
        },
        "messages": [...]
    }
}
```

### Formato B — `conversation_status_changed`

**ATENÇÃO:** O body É a conversa diretamente. Não há wrapper `conversation`.

```python
body = {
    "event": "conversation_status_changed",
    "id": 2159,                 # conversa_id está aqui, não em body.conversation.id
    "status": "resolved",       # status está aqui, não em body.conversation.status
    "inbox_id": 91,
    "labels": [],
    "custom_attributes": {},
    "messages": [
        {
            "content": "De 0 a 10...",
            "content_attributes": {"nps_survey": True}  # mensagem NPS automática
        }
    ],
    "meta": {
        "sender": {"name": "Cliente", "id": 10685},
        "assignee": {"name": "Camila", "id": 66}
    }
}
```

### Tipos de attachment
```python
attachment = {
    "file_type": "image" | "audio" | "video" | "file" | "location" | "sticker" | "contact",
    "data_url": "https://...",   # URL para download
    "thumb_url": "https://...",  # thumbnail (só imagens)
    "file_size": 313301,
    "fallback_title": "...",     # nome/telefone para tipo "contact"
    "meta": {                    # para tipo "contact"
        "firstName": "João",
        "lastName": "Silva"
    }
}
```

---

## Bugs Conhecidos do n8n que NÃO Devem ser Replicados

1. **`em_atendimento` incompleto:** O n8n lê apenas de `conversation.custom_attributes.atendimento`. Nos webhooks reais, esse campo frequentemente está ausente na conversa mas presente em `sender.custom_attributes.atendimento` ou nas `labels`. A implementação Python deve checar as três fontes, priorizando labels.

2. **`sender_type` ausente:** Para mensagens de clientes, `body.sender.type` não existe. Detecção deve ser por `identifier` ou `phone_number`.

3. **`status_changed` mal parseado:** O body do `conversation_status_changed` é a conversa diretamente — `body.get('status')`, não `body.get('conversation', {}).get('status')`.

---

## Arquitetura Alvo

### Fluxo Completo

```
SPX Webhook POST /webhook/spx
        │
        ▼
normalizar(body) → Evento
        │
        ├─ ignorar          → return 200 (sem processamento)
        │
        ├─ marcar_atend.    → spx.marcar_atendimento(True)
        │                      spx.adicionar_label("atendimento")
        │
        ├─ limpar_atend.    → spx.marcar_atendimento(False)
        │                      spx.remover_labels()
        │                      memoria.limpar(conversa_id)
        │
        ├─ copiloto         → spx.buscar_historico()
        │                      copiloto.processar()
        │                      spx.enviar_privado()
        │
        └─ agente_clara
                │
                ├─ tem mídia? ──► pipeline_midia()
                │                    audio → whisper_transcrever()
                │                    imagem → vision_descrever()
                │                    → spx.enviar_privado(descricao)
                │                    → texto_para_clara = descricao
                │
                └─ buffer_debounce(conversa_id, texto)
                            │
                            └─ (após 15s, última mensagem do buffer)
                                        │
                                        ▼
                                 clara.processar()
                                        │
                                        ▼
                                 humanizador(resposta)
                                        │
                                        ▼
                                 spx.enviar_mensagens([msg1, msg2])
```

### Regras de Roteamento Completas

```python
def determinar_rota(evento) -> str:
    # Bloqueios imediatos (ordem importa)
    if evento.is_status_changed:
        return "limpar_atendimento" if evento.status == "resolved" else "ignorar"
    if evento.message_type == "activity":           # type 2
        return "ignorar"
    if evento.content_attrs.get("nps_survey"):
        return "ignorar"
    if evento.sender_type == "agent_bot":
        return "ignorar"
    if "@g.us" in (evento.source_id or "") or "@g.us" in (evento.contact_source_id or ""):
        return "ignorar"

    # Cliente
    if evento.sender_type == "contact":
        if evento.em_atendimento:
            return "ignorar"
        if not evento.content and not evento.tem_anexo:
            return "ignorar"
        return "agente_clara"   # inclui mídia — pipeline trata internamente

    # Atendente
    if evento.sender_type == "user":
        if evento.private:
            return "copiloto" if "#tozi" in evento.content.lower() else "ignorar"
        return "marcar_atendimento"

    return "ignorar"
```

**Detecção de `em_atendimento` (checar as três fontes):**
```python
def detectar_em_atendimento(body, sender, conversa) -> bool:
    # 1. Labels da conversa (mais confiável)
    if "atendimento" in conversa.get("labels", []):
        return True
    # 2. Custom attributes da conversa
    if conversa.get("custom_attributes", {}).get("atendimento") is True:
        return True
    # 3. Custom attributes do contato/sender
    if sender.get("custom_attributes", {}).get("atendimento") is True:
        return True
    return False
```

**Detecção de `sender_type` (sem depender do campo `type`):**
```python
def detectar_sender_type(sender: dict, message_type: str) -> str:
    tipo = (sender.get("type") or "").lower()
    if tipo == "agent_bot":
        return "agent_bot"
    if tipo == "user":
        return "user"
    if tipo == "contact":
        return "contact"
    # Fallback: contato não tem campo "type"
    if sender.get("phone_number") or sender.get("identifier"):
        return "contact"
    if message_type == "incoming":
        return "contact"
    return "unknown"
```

---

## Buffer / Debounce

O n8n usa Redis + wait de 15s para agrupar mensagens enviadas em sequência rápida pelo cliente. O comportamento esperado:

- Cliente manda "Oi" → entra no buffer, inicia timer de 15s
- Cliente manda "tudo bem?" 3s depois → entra no buffer, reinicia timer
- Timer expira → lê todo o buffer, processa tudo junto como uma mensagem
- Se buffer não for a última mensagem (cliente mandou mais depois do timer) → ignora, aguarda o próximo ciclo

**Implementação Python (asyncio + Redis):**

```python
# buffer.py
import asyncio
import redis.asyncio as aioredis
import json

DEBOUNCE_SEGUNDOS = 15

async def push_e_debounce(conversa_id: int, texto: str, callback) -> None:
    """
    Adiciona texto ao buffer e agenda processamento.
    Se nova mensagem chegar antes do timer, o timer anterior é cancelado.
    """
    r = aioredis.from_url(REDIS_URL)
    chave_buffer = f"buffer:{conversa_id}"
    chave_lock   = f"buffer_lock:{conversa_id}"

    # Adiciona ao buffer
    await r.rpush(chave_buffer, texto)
    await r.expire(chave_buffer, 300)

    # Cancela timer anterior se existir
    lock = await r.get(chave_lock)
    if lock:
        await r.delete(chave_lock)

    # Marca timer ativo
    await r.set(chave_lock, "1", ex=DEBOUNCE_SEGUNDOS + 5)
    await asyncio.sleep(DEBOUNCE_SEGUNDOS)

    # Verifica se ainda somos o timer ativo
    if not await r.exists(chave_lock):
        return  # outro timer assumiu

    # Lê e limpa o buffer
    mensagens_raw = await r.lrange(chave_buffer, 0, -1)
    await r.delete(chave_buffer)
    await r.delete(chave_lock)

    if not mensagens_raw:
        return

    mensagens = [m.decode() if isinstance(m, bytes) else m for m in mensagens_raw]
    texto_combinado = "\n".join(mensagens)
    await callback(conversa_id, texto_combinado)
```

---

## Pipeline de Mídia

Quando `sender_type == "contact"` e há anexo, antes de chamar a Clara:

```
attachment.file_type == "audio"
    → Download do arquivo (GET data_url com auth SPX)
    → Transcrição via OpenAI Whisper (whisper-1)
    → Enviar nota privada: "🎤 Áudio transcrito: {transcricao}"
    → texto_para_clara = transcricao

attachment.file_type == "image"
    → Análise via GPT-4o (vision)
    → Prompt: descrever o que vê, focando em imóvel, placa, texto visível
    → Enviar nota privada: "🖼️ Imagem: {descricao}"
    → texto_para_clara = descricao (com legenda se houver)

outros tipos (video, file, location, sticker, contact)
    → Não processar, passar texto_humano direto para Clara
    → texto_para_clara = "[Vídeo enviado pelo cliente]" etc.
```

**Nota privada de mídia vai ANTES da Clara responder.** O atendente humano precisa saber o que chegou antes de ver a resposta da Clara.

**Download de mídia do SPX requer autenticação:**
```python
headers = {"api_access_token": SPX_BOT_TOKEN}
response = await httpx.get(attachment["data_url"], headers=headers)
```

---

## Humanizador

Após a Clara gerar a resposta, um segundo LLM (modelo leve) quebra o texto em 1-2 mensagens curtas para WhatsApp.

**Regras do humanizador:**
- Máximo 2 mensagens
- Cada mensagem: máximo 3 frases
- Remover formalidade excessiva
- Não alterar conteúdo, só formato
- Emoji só se já estava na resposta original
- Quebrar em 2 quando: há duas partes distintas, ou mensagem ficaria com mais de 3 frases

**Output esperado:** lista de strings `["mensagem 1", "mensagem 2"]`

**Envio em loop:** cada string é enviada como POST separado para o SPX, com delay de 500ms entre cada uma (simula digitação humana).

---

## Memória das Conversas

**Backend:** Redis  
**Chave:** `historico:{conversa_id}`  
**TTL:** 24h  
**Janela:** últimas 40 mensagens (equivale ao windowSize do n8n)  
**Formato:** lista de dicts no formato Anthropic messages

```python
[
    {"role": "user",      "content": "Oie"},
    {"role": "assistant", "content": "Olá! Tudo bem? Como posso te ajudar?"},
    {"role": "user",      "content": [{"type": "tool_result", ...}]},  # após tool call
]
```

**Limpar ao resolver:** quando `conversation_status_changed` com `status: resolved`, deletar a chave.

---

## Loop de Agente (Anthropic SDK)

**Padrão para todos os agentes:**

```python
import anthropic

client = anthropic.Anthropic()

async def executar_agente(system, historico, tools, tool_handler, model="claude-sonnet-4-5"):
    while True:
        resposta = client.messages.create(
            model=model,
            system=system,
            messages=historico,
            tools=tools,
            max_tokens=1024,
        )

        historico.append({"role": "assistant", "content": resposta.content})

        if resposta.stop_reason == "end_turn":
            texto = next((b.text for b in resposta.content if b.type == "text"), "")
            return texto, historico

        if resposta.stop_reason == "tool_use":
            resultados = []
            for bloco in resposta.content:
                if bloco.type == "tool_use":
                    resultado = await tool_handler(bloco.name, bloco.input)
                    resultados.append({
                        "type": "tool_result",
                        "tool_use_id": bloco.id,
                        "content": str(resultado),
                    })
            historico.append({"role": "user", "content": resultados})
            continue

        break  # stop_reason inesperado

    return "Não consegui processar no momento.", historico
```

---

## Agentes

### Clara (pré-atendimento)

**Papel:** Primeira voz que o cliente ouve. Recepciona, entende a demanda, qualifica o lead, confirma nome, chama `atribuir_atendimento` quando pronto.

**Quando atribuir:**
- Dentro do horário: assim que entender o motivo e confirmar o nome
- Fora do horário: após qualificar mais profundamente (1 pergunta por vez)
- Suporte: imediato após entender o problema

**Tools da Clara:**
- `buscar_imoveis` — chama Vista API
- `buscar_localizacao` — converte referência geográfica em coordenadas
- `faq_tozi` — base de conhecimento (vector store)
- `atribuir_atendimento` — subagente que enriquece e atribui para Camila

**Contexto injetado dinamicamente no system prompt:**
```
nome_cliente: {body.conversation.meta.sender.name}
em_atendimento: {True/False}
resumo_previo: {body.conversation.custom_attributes.resumo ou ""}
horario: {"dentro" | "fora"} do expediente
data_hora_atual: {datetime.now(TZ).strftime(...)}
```

**Horário comercial Tozi (fuso America/Cuiaba = UTC-4):**
```
Seg-Sex: 07:30-11:30 e 13:30-17:30
Sábado:  09:00-11:30
Domingo: fechado
```

**O que Clara NÃO faz:** buscar imóveis diretamente para o cliente, agendar visitas, negociar valores, resolver suporte, prometer prazos.

**O que Clara faz:** o `atribuir_atendimento` (subagente) busca imóveis para montar a sugestão no resumo privado.

### Copiloto (assistente interno)

**Papel:** Assistente dos atendentes, invisível para o cliente. Acionado via `#tozi` em nota privada.

**Sem memória:** busca histórico completo via API do SPX a cada chamada. Não usa Redis.

**Tools do Copiloto:**
- `buscar_imoveis`
- `buscar_localizacao`
- `faq_tozi`
- `consultar_conversa` — retorna histórico formatado da conversa atual

**Comportamento:** direto e acionável. Se pode buscar, busca. Não faz perguntas ao atendente.

### Atribuidor (subagente da Clara)

**Papel:** Executado como tool da Clara. Enriquece o handoff, busca imóveis se aplicável, envia resumo e sugestão como notas privadas, atribui para Camila.

**Não é um agente separado no FastAPI** — é uma tool complexa que pode chamar outras tools internamente.

**Sequência:**
1. Analisa o contexto que a Clara passou
2. Se tem critérios de imóvel: `buscar_localizacao` (se referência geográfica) → `buscar_imoveis`
3. Se é suporte com nome: `consultar_cadastro`
4. `atribuir_atendimento_spx`:
   - Envia resumo como nota privada
   - Envia sugestão como nota privada (se houver)
   - Atribui conversa para Camila (agent_id: 66)
   - Atualiza `custom_attributes.resumo` na conversa

---

## Estrutura do Projeto

```
tozi-agent/
├── main.py
├── normalizar.py
├── config.py
├── memoria.py
├── buffer.py
├── spx.py
├── midia.py
├── humanizador.py
│
├── agentes/
│   ├── base.py
│   ├── clara.py
│   ├── copiloto.py
│   └── prompts/
│       ├── clara.md
│       └── copiloto.md
│
├── tools/
│   ├── __init__.py
│   ├── schemas.py
│   ├── buscar_imoveis.py
│   ├── buscar_localizacao.py
│   ├── faq_tozi.py
│   ├── atribuir_atendimento.py
│   └── consultar_conversa.py
│
├── tests/
│   ├── webhooks/
│   │   ├── w1_texto_incoming.json
│   │   ├── w2_imagem_incoming.json
│   │   ├── w3_outgoing_publico.json
│   │   ├── w4_outgoing_privado_tozi.json
│   │   └── w5_status_resolved.json
│   ├── test_normalizar.py
│   └── test_tools.py
│
├── requirements.txt
└── .env
```

---

## Variáveis de Ambiente

```env
# Anthropic
ANTHROPIC_API_KEY=sk-ant-...

# SPX
SPX_BASE_URL=https://chat.simplexsolucoes.com.br
SPX_ACCOUNT_ID=6
SPX_BOT_TOKEN=...

# OpenAI (Whisper + Vision)
OPENAI_API_KEY=sk-...

# Redis
REDIS_URL=redis://localhost:6379

# Vista
VISTA_BASE_URL=https://toz19328-rest.vistahost.com.br
VISTA_API_KEY=...

# Google Maps
GOOGLE_MAPS_KEY=...

# Ambiente
AMBIENTE=desenvolvimento
CONVERSA_TESTE_ID=2159
```

---

## Ambiente de Teste

**Estratégia:** Inbox separada no ChatWoot para teste, em paralelo com produção (n8n continua rodando).

Em `AMBIENTE=desenvolvimento`, o sistema só processa `CONVERSA_TESTE_ID`. Todas as outras chegam e retornam 200 sem processar.

```python
def deve_processar(conversa_id: int) -> bool:
    if os.getenv("AMBIENTE") == "producao":
        return True
    return conversa_id == int(os.getenv("CONVERSA_TESTE_ID", "0"))
```

**Simulação de webhook:**
```bash
# Rodar servidor
uvicorn main:app --reload --port 8000

# Simular mensagem de cliente
curl -X POST http://localhost:8000/webhook/spx \
     -H "Content-Type: application/json" \
     -d @tests/webhooks/w1_texto_incoming.json
```

---

## Testes Obrigatórios (Fase 0)

O seguinte deve passar antes de qualquer código de agente:

```python
# tests/test_normalizar.py

def test_w1_texto_sem_atendimento_vai_para_clara():
    # custom_attributes não tem atendimento, mas labels tem "atendimento"
    # resultado esperado: ignorar (em_atendimento via labels)
    ...

def test_w1_sem_label_atendimento_vai_para_clara():
    # mesmo webhook sem a label "atendimento"
    # resultado esperado: agente_clara
    ...

def test_w2_imagem_sem_atendimento_vai_para_clara():
    # tem_anexo = True, file_type = "image"
    # resultado esperado: agente_clara
    ...

def test_w3_outgoing_publico_marca_atendimento():
    # sender_type = user, private = False
    # resultado esperado: marcar_atendimento
    ...

def test_w4_tozi_privado_vai_para_copiloto():
    # sender_type = user, private = True, content tem "#tozi"
    # resultado esperado: copiloto
    # texto limpo: sem "#tozi"
    ...

def test_w5_resolved_limpa_atendimento():
    # event = conversation_status_changed, status = resolved
    # resultado esperado: limpar_atendimento
    # conversa_id vem de body.id, não de body.conversation.id
    ...

def test_grupo_ignorado():
    # contact_inbox.source_id contém "@g.us"
    # resultado esperado: ignorar
    ...

def test_agent_bot_ignorado():
    # sender.type = "agent_bot"
    # resultado esperado: ignorar
    ...

def test_sender_sem_type_detectado_como_contact():
    # sender não tem campo "type" mas tem "phone_number"
    # resultado esperado: contact detectado, rotar para agente_clara
    ...
```

---

## Roadmap de Migração

### Fase 0 — Base (começar aqui)
Implementar e testar sem chamar nenhuma API externa:
- `normalizar.py` com todos os casos de roteamento
- `config.py` com horário comercial
- `main.py` com webhook recebendo e roteando (sem processar ainda)
- `tests/webhooks/` com os 5 JSONs reais
- `test_normalizar.py` todos passando

**Critério:** `pytest tests/test_normalizar.py` — 100% pass.

### Fase 1 — Clara funcionando
- `memoria.py` (Redis)
- `spx.py` (enviar mensagem, enviar privado, marcar atendimento, labels)
- `buffer.py` (debounce 15s)
- `agentes/base.py` (loop Anthropic SDK)
- `agentes/clara.py`
- `agentes/prompts/clara.md` (copiar do n8n)
- `tools/` completo
- `humanizador.py`
- Integrar tudo no `main.py`

**Critério:** mandar mensagem na conversa de teste → Clara responde → Camila recebe o lead.

### Fase 2 — Copiloto funcionando
- `agentes/copiloto.py`
- `agentes/prompts/copiloto.md`
- `tools/consultar_conversa.py`

**Critério:** digitar `#tozi pergunta` na conversa de teste → copiloto responde em privado.

### Fase 3 — Pipeline de mídia
- `midia.py` (Whisper + Vision)
- Integrar no fluxo da Clara

**Critério:** mandar áudio → nota privada com transcrição → Clara responde baseada no áudio.

### Fase 4 — Deploy e virada para produção
- Servidor em produção (VPS ou Railway)
- Webhook da inbox principal apontando para Python
- Remover webhook do n8n

---

## O que NÃO Implementar (ainda)

- Consultar cadastro de clientes (endpoint Vista não definido)
- Agendamento via Google Calendar
- Simulação de financiamento
- Dashboard de métricas
- Inngest (adicionar durabilidade só após sistema estável)

---

## Convenções de Código

- Async em tudo que faz I/O (httpx, redis, anthropic)
- Sem prints — usar `logging` com `conversa_id` em todo log
- Erros nunca silenciados — capturar, logar com traceback, responder 200 pro webhook
- `private: True` é boolean, não string, na API do ChatWoot
- Todos os POSTs para SPX com `Content-Type: application/json`
- Respostas do webhook sempre retornam 200, mesmo em erro (SPX não reenvia se der 4xx/5xx)
