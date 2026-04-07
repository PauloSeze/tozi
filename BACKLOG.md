# Tozi SDR — Backlog de Desenvolvimento

**Última atualização:** 09/02/2026

---

## Legenda

- 🔴 **Não iniciado**
- 🟡 **Em análise/design**
- 🟢 **Em desenvolvimento**
- ✅ **Concluído**

---

## 1. Tools Pendentes

### 1.1 Tool: Consultar Cadastro de Clientes
**Status:** 🔴 Não iniciado
**Prioridade:** Alta

**Descrição:**
Buscar cliente na base Vista pelo nome. Usada pelo Atribuidor em casos de suporte para localizar inquilinos ou proprietários.

**Requisitos:**
- [ ] Definir endpoint Vista para busca de clientes
- [ ] Mapear campos retornados (nome, telefone, imóvel, status)
- [ ] Criar subworkflow `Tozi TOOL - Consultar Cadastro`
- [ ] Integrar no Atribuidor e Copiloto
- [ ] Documentar schema de input/output

**Uso esperado:**
```json
{
  "nome": "João Silva"
}
```

**Retorno esperado:**
```json
{
  "encontrado": true,
  "cliente": {
    "nome": "João Silva Santos",
    "tipo": "inquilino",
    "imovel": "Rua das Figueiras, 123",
    "contrato": "ativo",
    "contato": "(66) 99999-1234"
  }
}
```

---

### 1.2 Tool: Consultar Grupo de Gerentes
**Status:** 🔴 Não iniciado
**Prioridade:** Média

**Descrição:**
Quando o Copiloto não encontra resposta na FAQ, ele pode enviar a pergunta para um grupo de WhatsApp/ChatWoot com os gerentes e aguardar resposta.

**Requisitos:**
- [ ] Criar grupo de gerentes no ChatWoot (ou WhatsApp)
- [ ] Definir formato de pergunta enviada
- [ ] Implementar webhook de resposta dos gerentes
- [ ] Criar lógica de timeout (resposta não recebida)
- [ ] Criar subworkflow `Tozi TOOL - Perguntar Gerentes`
- [ ] Integrar no Copiloto como fallback da FAQ

**Fluxo:**
```
Copiloto → FAQ não tem resposta
        → Envia pergunta para grupo de gerentes
        → Aguarda resposta (timeout: X minutos)
        → Recebe resposta → Responde atendente
        → Não recebe → Informa que precisa aguardar gerência
```

**Considerações:**
- A resposta do gerente deve ser capturada e armazenada para futura FAQ
- Evitar spam no grupo — só perguntas genuínas não encontradas

---

## 2. Agentes Novos

### 2.1 Agente: Follow-up
**Status:** 🔴 Não iniciado
**Prioridade:** Média

**Descrição:**
Agente que aciona clientes ociosos (conversas sem resposta há X dias) para retomar o atendimento.

**Requisitos:**
- [ ] Definir critérios de "cliente ocioso" (dias sem interação, status, labels)
- [ ] Criar scheduler (cron) para varredura diária
- [ ] Definir mensagens de follow-up por tipo de demanda
- [ ] Implementar limite de tentativas (máx. 2-3 follow-ups)
- [ ] Criar workflow `Tozi Follow-up - Clientes Ociosos`
- [ ] Integrar com labels do ChatWoot para tracking

**Critérios sugeridos:**
- Conversas abertas há mais de 3 dias sem resposta do cliente
- Conversas com label "aguardando_cliente" há mais de 2 dias
- Excluir conversas já em atendimento ativo

**Mensagens por cenário:**
- **Locação/Venda:** "Oi [nome]! Tudo bem? Ainda está procurando [tipo de imóvel]? Posso ajudar com mais opções."
- **Suporte:** "Oi [nome]! Conseguiu resolver a questão do [problema]? Estamos à disposição."
- **Genérico:** "Oi [nome]! Vi que conversamos há alguns dias. Posso ajudar com algo?"

**Limites:**
- Máximo 2 follow-ups por conversa
- Intervalo mínimo de 2 dias entre follow-ups
- Não enviar fora do horário comercial

---

## 3. Sistema de Avaliação (Evaluation)

### 3.1 Evaluation: Conversas IA ↔ Cliente
**Status:** 🔴 Não iniciado
**Prioridade:** Alta

**Descrição:**
Avaliar a qualidade das interações entre os agentes de IA (Clara, Copiloto) e os clientes.

**Métricas propostas:**
- **Clareza:** Mensagens foram claras e compreensíveis?
- **Relevância:** Resposta foi pertinente à pergunta?
- **Tom:** Tom foi adequado (não robótico, não informal demais)?
- **Eficiência:** Quantas trocas até resolver/atribuir?
- **Erros:** Informações incorretas, promessas indevidas?
- **Handoff:** Atribuição foi no momento certo?

**Implementação:**
- [ ] Definir schema de avaliação (1-5 ou labels)
- [ ] Criar pipeline de avaliação (batch ou streaming)
- [ ] Escolher método: LLM-as-judge ou humano
- [ ] Criar dashboard de métricas
- [ ] Definir thresholds de alerta (qualidade abaixo de X)

**Formato de saída:**
```json
{
  "conversa_id": 2159,
  "data_avaliacao": "2026-02-09",
  "agente": "Clara",
  "metricas": {
    "clareza": 4,
    "relevancia": 5,
    "tom": 4,
    "eficiencia": 3,
    "erros": 0,
    "handoff_adequado": true
  },
  "nota_geral": 4.2,
  "comentarios": "Qualificação demorou 5 trocas, poderia ser mais direta."
}
```

---

### 3.2 Evaluation: Conversas Atendente ↔ Cliente
**Status:** 🔴 Não iniciado
**Prioridade:** Média

**Descrição:**
Avaliar a qualidade das interações entre atendentes humanos e clientes.

**Métricas propostas:**
- **Tempo de resposta:** Quanto tempo até responder?
- **Clareza:** Mensagens foram claras?
- **Proatividade:** Ofereceu soluções ou só respondeu?
- **Conhecimento:** Demonstrou conhecimento do produto/processo?
- **Fechamento:** Conversa evoluiu para visita/contrato?
- **Tom:** Profissional e cordial?

**Implementação:**
- [ ] Definir schema de avaliação
- [ ] Criar agente avaliador (Copiloto v2 ou dedicado)
- [ ] Rodar avaliação em batch (diário/semanal)
- [ ] Gerar relatórios por atendente
- [ ] Criar alertas para baixa performance

**Usos:**
- Feedback para treinamento de equipe
- Identificação de gaps de conhecimento
- Benchmark entre atendentes
- Input para atualização de FAQ/Playbooks

---

## 4. Portal de Gestão

### 4.1 Portal: FAQ e Playbooks
**Status:** 🔴 Não iniciado
**Prioridade:** Média

**Descrição:**
Interface web para gerentes atualizarem a base de conhecimento (FAQ) e playbooks de atendimento sem precisar de desenvolvedor.

**Funcionalidades:**

#### FAQ
- [ ] Listar perguntas/respostas existentes
- [ ] Adicionar nova pergunta/resposta
- [ ] Editar pergunta/resposta existente
- [ ] Excluir (soft delete) pergunta
- [ ] Categorizar por tema (locação, venda, suporte, empresa)
- [ ] Histórico de alterações
- [ ] Preview de como o agente vê a FAQ

#### Playbooks
- [ ] Listar playbooks por cenário
- [ ] Editar fluxos de atendimento
- [ ] Definir perguntas obrigatórias por tipo de demanda
- [ ] Configurar mensagens padrão de follow-up
- [ ] Configurar horários e limites

#### Gestão
- [ ] Dashboard de uso da FAQ (quais perguntas mais consultadas)
- [ ] Perguntas não respondidas (input para novas FAQs)
- [ ] Métricas de avaliação dos agentes
- [ ] Configurações gerais (horário comercial, timeouts)

**Stack sugerida:**
- Frontend: React + TypeScript (mesmo do GestorEnergy)
- Backend: FastAPI ou Supabase
- Autenticação: Supabase Auth ou OAuth
- Storage: PostgreSQL + Vector Store para FAQ

**Fluxo de atualização:**
```
Gerente edita FAQ no portal
        → Webhook dispara rebuild do vector store
        → Agentes passam a usar nova versão
        → Log de auditoria registrado
```

---

## 5. Melhorias Futuras

### 5.1 Copiloto v2 (Observador)
**Status:** 🔴 Não iniciado
**Prioridade:** Baixa (pós-evaluation)

Copiloto que observa todas as conversas e avalia silenciosamente, podendo:
- Sugerir correções em mensagens do atendente
- Notificar gestor sobre situações críticas
- Avaliar qualidade das respostas da Clara
- Detectar oportunidades comerciais perdidas

### 5.2 Processamento de Mídia Avançado
**Status:** 🔴 Não iniciado
**Prioridade:** Baixa

- Geocode reverso para localizações compartilhadas
- Transcrição de vídeos curtos
- Extração de texto de documentos (OCR)

### 5.3 Integração com CRM Vista
**Status:** 🔴 Não iniciado
**Prioridade:** Baixa

- Criar lead automaticamente no Vista após qualificação
- Sincronizar status de atendimento
- Registrar histórico de interações

---

## Priorização Sugerida

| # | Item | Impacto | Esforço | Prioridade |
|---|------|---------|---------|------------|
| 1 | Tool Consultar Cadastro | Alto | Baixo | 🔥 Alta |
| 2 | Evaluation IA ↔ Cliente | Alto | Médio | 🔥 Alta |
| 3 | Agente Follow-up | Médio | Médio | ⚡ Média |
| 4 | Evaluation Atendente ↔ Cliente | Médio | Médio | ⚡ Média |
| 5 | Tool Perguntar Gerentes | Médio | Médio | ⚡ Média |
| 6 | Portal FAQ/Playbooks | Alto | Alto | ⚡ Média |
| 7 | Copiloto v2 Observador | Alto | Alto | 📋 Baixa |

---

## Notas

- O sistema de Evaluation deve ser implementado antes do Copiloto v2, pois fornece a base de métricas
- O Portal de FAQ pode começar simples (só FAQ) e evoluir para Playbooks
- A Tool de Gerentes pode usar o próprio ChatWoot como grupo interno
