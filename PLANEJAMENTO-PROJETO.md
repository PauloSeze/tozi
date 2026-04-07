# Tozi Imobiliaria - Planejamento de Projeto

**Cliente:** Tozi Imoveis (Sinop/MT)
**Contrato:** 36 meses | R$ 11.300,00/mes
**Data de inicio:** 16/03/2026 (segunda-feira)
**Documento:** Planejamento executivo pos-aceite

---

## 1. Resumo do Projeto

Tres frentes estrategicas paralelas:

| Frente | Investimento | Duracao Implantacao | Foco |
|--------|-------------|---------------------|------|
| IA Atendimento | R$ 5.600/mes | 12 meses (ciclo 1) | Vendas: SDR Passivo, Follow-up, SDR Ativo, VoxIA |
| IA Processos Internos | R$ 4.850/mes | 6 meses | Financeiro, Juridico, Gestao |
| Site | R$ 850/mes | Incluido | Criacao/manutencao do site |

**Contexto:** O SDR Passivo (Locacao) ja foi entregue em janeiro/2026 e esta parcialmente ativo. A proxima fase retoma e expande esse trabalho.

---

## 2. Formato de Trabalho

### 2.1 Modelo de Entregas
- **Sprints semanais** com entregas progressivas
- **Validacao ao final de cada sprint** com o ponto focal da Tozi
- **Documentacao tecnica** atualizada a cada entrega

### 2.2 Reunioes

| Reuniao | Frequencia | Duracao | Participantes | Objetivo |
|---------|-----------|---------|---------------|----------|
| **Kickoff** | Unica (16/03) | 1h30 | Paulo + Gestao Tozi | Alinhamento geral, expectativas, acessos, cronograma |
| **Weekly** | Semanal (toda segunda) | 30min | Paulo + Ponto focal Tozi | Status, bloqueios, proximos passos |
| **Review de Fase** | A cada marco | 1h | Paulo + Gestao Tozi | Demo de entrega, feedback, aceite da fase |
| **Treinamento** | Por modulo | 1h-2h | Paulo + Usuarios do modulo | Capacitacao pratica |
| **Retrospectiva Trimestral** | A cada 3 meses | 1h | Paulo + Gestao Tozi | Metricas, ajustes estrategicos, roadmap |

### 2.3 Comunicacao
- **Canal principal:** Grupo no WhatsApp (Simplex + Tozi)
- **Demandas tecnicas:** Tickets via ChatWoot ou email
- **Documentacao:** Pasta compartilhada (Google Drive ou similar)
- **Urgencias:** WhatsApp direto com Paulo

### 2.4 Ponto Focal Tozi
- Definir 1 pessoa como ponto focal (sugestao: Camila ou supervisao)
- Responsavel por: validar entregas, fornecer acessos, alinhar equipe interna

---

## 3. Cronograma Detalhado - IA Atendimento

### FASE 1: SDR Passivo - Reativacao e Expansao (16/03 a 10/04)

**Objetivo:** Reativar o SDR Passivo (Locacao) e expandir para Vendas, Juridico e Financeiro.

| Semana | Periodo | Atividades | Entregavel | Validacao |
|--------|---------|-----------|------------|-----------|
| **S1** | 16/03 - 20/03 | Kickoff geral; Revisao dos fluxos ja entregues (Clara, Atribuidor, Copiloto); Levantamento de ajustes pedidos pela supervisao | Ata de kickoff; Lista de ajustes necessarios | Reuniao presencial/call |
| **S2** | 23/03 - 27/03 | Ajustes na IA (prompts, fluxos); Reativacao oficial do SDR Passivo - Locacao; Testes controlados com leads reais | SDR Passivo Locacao reativado | Monitoramento conjunto |
| **S3** | 30/03 - 03/04 | Mapeamento do atendimento de Vendas; Ajuste de prompts e rotas para Vendas; Configuracao de times no ChatWoot | SDR Passivo expandido para Vendas | Demo + teste |
| **S4** | 06/04 - 10/04 | Mapeamento de Juridico e Financeiro (atendimento externo); Configuracao de rotas e triagem; Ativacao completa do SDR Passivo | SDR Passivo ativo em todos os departamentos | **MARCO 1: Review de Fase** |

**Treinamento T1 (semana de 06/04):** Equipe de locacao + vendas — como funciona a Clara, como receber leads, como usar o Copiloto (1h)

---

### FASE 2: Follow-up Automatizado (13/04 a 08/05)

**Objetivo:** Automatizar recontato com leads que esfriaram.

| Semana | Periodo | Atividades | Entregavel | Validacao |
|--------|---------|-----------|------------|-----------|
| **S5** | 13/04 - 17/04 | Definicao de criterios de ociosidade com Tozi; Estruturacao dos fluxos de follow-up; Criacao de mensagens por cenario | Documento de regras de follow-up aprovado | Aprovacao do ponto focal |
| **S6** | 20/04 - 24/04 | Implementacao dos gatilhos automaticos (cron + ChatWoot); Logica de limites (max tentativas, horarios) | Workflow n8n de follow-up | Teste em sandbox |
| **S7** | 27/04 - 01/05 | Testes de recuperacao de leads com dados reais; Monitoramento de respostas; Ajustes de mensagens | Follow-up em teste controlado | Monitoramento conjunto |
| **S8** | 04/05 - 08/05 | Ajustes finais; Ativacao oficial | Follow-up automatizado ativo | **MARCO 2: Review de Fase** |

**Treinamento T2 (semana de 04/05):** Equipe — como acompanhar follow-ups, como desativar para leads especificos (30min)

---

### FASE 3: SDR Ativo / BDR - Estruturacao (11/05 a 05/06)

**Objetivo:** Prospectar e aquecer leads ativamente via WhatsApp.

| Semana | Periodo | Atividades | Entregavel | Validacao |
|--------|---------|-----------|------------|-----------|
| **S9** | 11/05 - 15/05 | Organizacao da base de leads existente; Definicao de segmentos e prioridades; Limpeza de dados | Base de leads organizada e segmentada | Aprovacao da gestao |
| **S10** | 18/05 - 22/05 | Definicao da abordagem IA por segmento; Criacao de scripts/prompts de prospecao; Configuracao de fluxos n8n | Prompts e fluxos de BDR prontos | Review tecnico |
| **S11** | 25/05 - 29/05 | Configuracao de disparos (volume, horarios, intervalos); Integracao com ChatWoot para tracking; Testes com amostra pequena | Disparos configurados e testados | Teste controlado |
| **S12** | 01/06 - 05/06 | Inicio oficial da prospeccao ativa; Monitoramento de respostas e conversao | BDR ativo e operando | **MARCO 3: Review de Fase** |

**Treinamento T3 (semana de 01/06):** Equipe comercial — como receber leads do BDR, pipeline de conversao (1h)

---

### FASE 4: BDR - Ajustes Operacionais (08/06 a 03/07)

**Objetivo:** Refinar a prospecao ativa com base nos primeiros resultados.

| Semana | Periodo | Atividades | Entregavel |
|--------|---------|-----------|------------|
| **S13** | 08/06 - 12/06 | Monitoramento de respostas e metricas de conversao | Relatorio de performance semana 1 |
| **S14** | 15/06 - 19/06 | Ajustes de abordagem baseados em dados | Prompts refinados |
| **S15** | 22/06 - 26/06 | Refinamento de qualificacao (criterios de lead quente) | Criterios atualizados |
| **S16** | 29/06 - 03/07 | Estabilizacao do fluxo ativo | **MARCO 4: BDR estavel** |

---

### FASE 5: VoxIA - Estrutura Tecnica (06/07 a 31/07)

**Objetivo:** Preparar infraestrutura para atendimento por voz com IA.

| Semana | Periodo | Atividades | Entregavel |
|--------|---------|-----------|------------|
| **S17** | 06/07 - 10/07 | Configuracao da infraestrutura de voz (provider, telefonia, APIs) | Infraestrutura provisionada |
| **S18** | 13/07 - 17/07 | Integracao com sistema de atendimento (ChatWoot/n8n) | Integracao funcional |
| **S19** | 20/07 - 24/07 | Criacao do fluxo de atendimento receptivo por voz | Fluxo receptivo pronto |
| **S20** | 27/07 - 31/07 | Testes tecnicos de qualidade de voz e compreensao | Relatorio de testes |

---

### FASE 6: VoxIA - Ativacao Receptiva (03/08 a 28/08)

**Objetivo:** Ativar atendimento por voz para chamadas recebidas.

| Semana | Periodo | Atividades | Entregavel |
|--------|---------|-----------|------------|
| **S21** | 03/08 - 07/08 | Ajustes de linguagem e tom de voz | Voz calibrada |
| **S22** | 10/08 - 14/08 | Testes de entendimento com cenarios reais | Relatorio de acuracia |
| **S23** | 17/08 - 21/08 | Correcoes finais | Sistema ajustado |
| **S24** | 24/08 - 28/08 | Ativacao oficial do atendimento por voz receptivo | **MARCO 5: VoxIA Receptivo ativo** |

**Treinamento T4 (semana de 24/08):** Equipe — como funciona o atendimento por voz, como escalar para humano (1h)

---

### FASE 7: VoxIA - Chamadas Ativas (31/08 a 23/10)

**Objetivo:** Implementar chamadas ativas por voz com IA.

| Semana | Periodo | Atividades | Entregavel |
|--------|---------|-----------|------------|
| **S25-26** | 31/08 - 11/09 | Definicao de roteiros; Configuracao de campanhas | Roteiros e campanhas |
| **S27-28** | 14/09 - 25/09 | Testes de chamadas ativas; Ajustes operacionais | Chamadas testadas |
| **S29-30** | 28/09 - 09/10 | Inicio oficial + monitoramento | VoxIA Ativo operando |
| **S31-32** | 12/10 - 23/10 | Ajustes de performance; Estabilizacao | **MARCO 6: VoxIA Completo** |

---

### FASE 8: Consolidacao (26/10/2026 a 13/03/2027)

| Periodo | Mes | Foco |
|---------|-----|------|
| **26/10 - 20/11** | Mes 9 (S33-36) | Ajustes integrados entre SDR + BDR + VoxIA; Padronizacao de abordagens |
| **23/11 - 19/12** | Mes 10 (S37-40) | Refinamento operacional: scripts, triagem, otimizacoes de fluxo |
| **22/12 - 16/01/2027** | Mes 11 (S41-44) | Estabilizacao geral: correcoes finais, testes de carga, ajustes finos |
| **19/01 - 13/03/2027** | Mes 12 (S45-52) | Monitoramento continuo; Preparacao para ciclo 2 (ano 2) |

**MARCO 7: Review de Primeiro Ciclo Completo** — 13/03/2027

---

## 4. Cronograma Detalhado - IA Processos Internos

> **Nota:** Esta frente roda em paralelo com a IA Atendimento.

### FASE A: Financeiro (16/03 a 08/05)

| Semana | Periodo | Atividades | Entregavel |
|--------|---------|-----------|------------|
| **S1-2** | 16/03 - 27/03 | Mapeamento dos processos financeiros atuais; Integracao com sistema imobiliario; Estruturacao de contas a receber | Documento de processos + integracao |
| **S3-4** | 30/03 - 10/04 | Geracao automatica de cobrancas; Lembretes e cobranca pos-vencimento | Automacao de cobranca ativa |
| **S5-6** | 13/04 - 24/04 | Conciliacao bancaria automatica; Cruzamento de contratos com extratos | Conciliacao automatizada |
| **S7-8** | 27/04 - 08/05 | Repasse ao proprietario automatizado; Projecao de fluxo de caixa | **MARCO A: Financeiro automatizado** |

**Treinamento TA (semana de 04/05):** Equipe financeira — como operar o novo fluxo (2h)

---

### FASE B: Juridico (11/05 a 03/07)

| Semana | Periodo | Atividades | Entregavel |
|--------|---------|-----------|------------|
| **S9-10** | 11/05 - 22/05 | Estruturacao dos modelos contratuais padrao; Parametrizacao de clausulas variaveis | Modelos contratuais prontos |
| **S11-12** | 25/05 - 05/06 | Geracao automatica de contratos; Integracao com assinatura digital | Contratos automatizados |
| **S13-14** | 08/06 - 19/06 | Leitura inteligente de contratos; Comparacao automatica com modelo padrao | IA de analise contratual |
| **S15-16** | 22/06 - 03/07 | Controle de prazos; Gestao de inadimplencia | **MARCO B: Juridico automatizado** |

**Treinamento TB (semana de 29/06):** Equipe juridica — como gerar contratos, como monitorar prazos (2h)

---

### FASE C: Gestao (06/07 a 28/08)

| Semana | Periodo | Atividades | Entregavel |
|--------|---------|-----------|------------|
| **S17-18** | 06/07 - 17/07 | Estruturacao de indicadores estrategicos; Consolidacao de base de dados | KPIs definidos + base unificada |
| **S19-20** | 20/07 - 31/07 | Dashboards executivos; Integracao dos dados financeiro + juridico | Dashboards operacionais |
| **S21-22** | 03/08 - 14/08 | Relatorios automaticos mensais | Relatorios configurados |
| **S23-24** | 17/08 - 28/08 | Analise preditiva (inadimplencia, risco, fluxo de caixa) | **MARCO C: Gestao com IA ativa** |

**Treinamento TC (semana de 24/08):** Gestao — como ler dashboards, como interpretar previsoes (1h30)

---

## 5. Marcos e Gates de Aprovacao

Cada marco requer **aceite formal** do ponto focal da Tozi antes de avancar:

| # | Marco | Data | Frente | Criterio de Aceite |
|---|-------|------|--------|-------------------|
| M1 | SDR Passivo ativo (todos os deptos) | **10/04** | Atendimento | Clara atendendo Locacao, Vendas, Juridico, Financeiro |
| M2 | Follow-up automatizado | **08/05** | Atendimento | Leads ociosos recebendo recontato automatico |
| M3 | BDR/SDR Ativo operando | **05/06** | Atendimento | Prospeccao ativa gerando leads qualificados |
| M4 | BDR estabilizado | **03/07** | Atendimento | Metricas de conversao estaveis |
| M5 | VoxIA Receptivo ativo | **28/08** | Atendimento | Ligacoes atendidas por IA com qualidade |
| M6 | VoxIA Completo (ativo + receptivo) | **23/10** | Atendimento | Chamadas ativas gerando resultados |
| M7 | Ciclo 1 completo | **13/03/2027** | Atendimento | Operacao estavel, metricas consolidadas |
| MA | Financeiro automatizado | **08/05** | Processos | Cobranca, conciliacao e repasse automaticos |
| MB | Juridico automatizado | **03/07** | Processos | Contratos gerados e monitorados por IA |
| MC | Gestao com IA | **28/08** | Processos | Dashboards e analise preditiva operacionais |

---

## 6. Calendario de Treinamentos

| # | Treinamento | Publico | Duracao | Data | Formato |
|---|------------|---------|---------|------|---------|
| T1 | SDR Passivo + Copiloto | Equipe Locacao + Vendas | 1h | Semana de **06/04** | Presencial/Call + gravacao |
| T2 | Follow-up | Equipe comercial | 30min | Semana de **04/05** | Call + doc |
| T3 | BDR / Prospeccao Ativa | Equipe comercial | 1h | Semana de **01/06** | Presencial/Call |
| T4 | VoxIA | Equipe geral | 1h | Semana de **24/08** | Presencial/Call |
| TA | Financeiro Automatizado | Equipe financeira | 2h | Semana de **04/05** | Presencial + hands-on |
| TB | Juridico Automatizado | Equipe juridica | 2h | Semana de **29/06** | Presencial + hands-on |
| TC | Dashboards e Gestao | Gestao/diretoria | 1h30 | Semana de **24/08** | Presencial + demo |

**Obs:** Todos os treinamentos incluem documentacao escrita (guia rapido) + gravacao da sessao.

---

## 7. Entregaveis por Fase

### Documentacao Entregue em Cada Fase
1. **Guia do usuario** — Como usar o modulo (linguagem nao-tecnica)
2. **Documentacao tecnica** — Fluxos, APIs, configuracoes (para manutencao)
3. **Video de treinamento** — Gravacao da sessao de capacitacao
4. **Relatorio de entrega** — O que foi feito, metricas iniciais, proximos passos

### Relatorios Recorrentes
- **Semanal (toda segunda):** Status breve (WhatsApp/email) — o que foi feito, o que vem na proxima semana
- **Mensal (primeira segunda do mes):** Relatorio de metricas — leads atendidos, conversao, tempo de resposta, qualidade IA
- **Trimestral:** Review estrategico — resultados vs. expectativas, ajustes de rota

### Calendario de Relatorios Mensais
| # | Relatorio Mensal | Data |
|---|-----------------|------|
| 1 | Mes 1 — SDR Passivo | 13/04 |
| 2 | Mes 2 — Follow-up | 11/05 |
| 3 | Mes 3 — BDR | 08/06 |
| 4 | Mes 4 — BDR Ajustes | 06/07 |
| 5 | Mes 5 — VoxIA Tecnico | 03/08 |
| 6 | Mes 6 — VoxIA Receptivo | 31/08 |

### Retrospectivas Trimestrais
| # | Retro | Data | Escopo |
|---|-------|------|--------|
| Q1 | Trimestre 1 | **08/06** | SDR Passivo + Follow-up + inicio BDR + Financeiro |
| Q2 | Trimestre 2 | **31/08** | BDR + VoxIA + Juridico + Gestao |
| Q3 | Trimestre 3 | **23/11** | Consolidacao geral |
| Q4 | Trimestre 4 / Review Anual | **13/03/2027** | Ciclo 1 completo, planejamento ciclo 2 |

---

## 8. Riscos e Mitigacoes

| Risco | Impacto | Probabilidade | Mitigacao |
|-------|---------|---------------|-----------|
| Resistencia da equipe ao uso da IA | Alto | Media | Treinamento pratico, envolvimento desde o kickoff, mostrar beneficios concretos |
| API Vista com limitacoes | Medio | Media | Mapear endpoints disponiveis na S1 (16-20/03), alternativas via scraping se necessario |
| Qualidade da IA abaixo do esperado | Alto | Baixa | Monitoramento continuo, ajustes de prompt, evaluation automatizado |
| Atraso no fornecimento de informacoes pela Tozi | Medio | Media | Definir ponto focal, SLA de resposta de 48h para solicitacoes |
| Infraestrutura de voz (VoxIA) com custos adicionais | Medio | Alta | Levantar custos ate 10/07, aprovar com Tozi antes de contratar |
| Integracao financeira com sistema legado | Alto | Media | Mapeamento detalhado ate 27/03, validar viabilidade tecnica antes de comprometer |

---

## 9. Premissas e Dependencias

### Premissas
- Tozi fornecera acesso a todos os sistemas necessarios (Vista CRM, contas bancarias, modelos de contrato)
- Ponto focal da Tozi disponivel para validacoes semanais
- Infraestrutura atual (ChatWoot, n8n, Redis) suficiente para as fases iniciais
- Custos de APIs externas (OpenAI, telefonia VoIP) sao responsabilidade da Tozi conforme contrato

### Dependencias da Tozi
| O que | Ate quando | Responsavel |
|-------|-----------|-------------|
| Acessos ao sistema imobiliario (financeiro/juridico) | **16/03** (kickoff) | TI Tozi |
| Extratos bancarios / acesso a contas para conciliacao | **13/04** | Financeiro Tozi |
| Aprovacao de scripts de follow-up | **13/04** | Gestao Tozi |
| Modelos de contrato atuais (locacao, venda, aditivo, distrato) | **11/05** | Juridico Tozi |
| Base de leads para prospeccao ativa | **11/05** | Comercial Tozi |
| Aprovacao de scripts de prospeccao | **18/05** | Gestao Tozi |
| Definicao de numero telefonico para VoxIA | **06/07** | Gestao Tozi |

---

## 10. Metricas de Sucesso

### IA Atendimento
| Metrica | Baseline (atual) | Meta Jun/26 | Meta Set/26 | Meta Mar/27 |
|---------|------------------|------------|------------|-------------|
| Tempo medio de primeira resposta | Manual (~15min) | < 30s (IA) | < 30s | < 30s |
| % leads qualificados automaticamente | 0% | 70% | 85% | 90% |
| Taxa de conversao lead → visita | A medir | +10% vs baseline | +20% | +30% |
| Leads recuperados via follow-up | 0 | 5/semana | 10/semana | 15/semana |
| Atendimentos por voz/dia | 0 | 0 | 10 receptivos | 20 (rec+ativo) |

### IA Processos Internos
| Metrica | Baseline | Meta Mai/26 | Meta Jul/26 | Meta Set/26 |
|---------|----------|------------|------------|-------------|
| Tempo de emissao de contrato | Manual (horas) | — | 5 minutos | 2 minutos |
| Conciliacao bancaria | Manual (dias) | Automatica | — | — |
| Repasse ao proprietario | Manual | Automatico | — | — |
| Contratos com prazos monitorados | 0% | — | 100% | 100% |
| Dashboards ativos | 0 | 0 | 0 | 3+ |

---

## 11. Visao Geral - Timeline

```
         MAR       ABR       MAI       JUN       JUL       AGO       SET       OUT
2026   16 23 30  06 13 20 27  04 11 18 25  01 08 15 22 29  06 13 20 27  03 10 17 24 31  07 14 21 28  05 12 19 26
       S1 S2 S3  S4 S5 S6 S7  S8 S9 S10S11 S12S13S14S15S16 S17S18S19S20 S21S22S23S24S25 S26S27S28   S29S30S31S32

ATENDIMENTO:
SDR Pas ██ ██ ██  M1
Follow  ·  ·  ·  ·  ██ ██ ██  M2
BDR     ·  ·  ·  ·  ·  ·  ·  ·  ██ ██ ██  M3 ██ ██ ██  M4
VoxIA   ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ██ ██ ██ ██  ██ ██ ██ M5 ██  ██ ██ ██   ██ ██ ██ M6

PROCESSOS:
Financ  ██ ██ ██  ██ ██ ██ ██  MA
Juridic ·  ·  ·  ·  ·  ·  ·  ·  ██ ██ ██  ██ ██ ██ ██  MB
Gestao  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ██ ██ ██ ██  ██ ██ ██ MC

MARCOS:
10/04 M1 | 08/05 M2+MA | 05/06 M3 | 03/07 M4+MB | 28/08 M5+MC | 23/10 M6

TREINOS:
06/04 T1 | 04/05 T2+TA | 01/06 T3 | 29/06 TB | 24/08 T4+TC

RETROS:
08/06 Q1 | 31/08 Q2 | 23/11 Q3 | 13/03/27 Q4
```

---

## 12. Proximos Passos Imediatos

| # | Acao | Responsavel | Prazo |
|---|------|-------------|-------|
| 1 | Assinatura do contrato | Gestao Tozi + Simplex | **16/03** |
| 2 | Reuniao de kickoff | Paulo | **16/03** |
| 3 | Tozi definir ponto focal | Gestao Tozi | **16/03** |
| 4 | Solicitar acessos (sistema financeiro, juridico) | Ponto focal Tozi | **16/03** |
| 5 | Criar grupo de comunicacao WhatsApp | Paulo | **16/03** |
| 6 | Enviar cronograma ao cliente | Paulo | **13/03** (pre-kickoff) |

---

## 13. Datas-Chave Resumo

| Data | Evento |
|------|--------|
| **16/03/2026** | Inicio do projeto / Kickoff |
| **10/04/2026** | Marco M1: SDR Passivo completo |
| **08/05/2026** | Marco M2 + MA: Follow-up + Financeiro |
| **05/06/2026** | Marco M3: BDR operando |
| **08/06/2026** | Retro Q1 (trimestre 1) |
| **03/07/2026** | Marco M4 + MB: BDR estavel + Juridico |
| **28/08/2026** | Marco M5 + MC: VoxIA Receptivo + Gestao |
| **31/08/2026** | Retro Q2 (trimestre 2) |
| **23/10/2026** | Marco M6: VoxIA Completo |
| **23/11/2026** | Retro Q3 (trimestre 3) |
| **13/03/2027** | Marco M7: Ciclo 1 completo / Retro Q4 |

---

*Documento gerado em 12/03/2026 — Simplex Solucoes Tecnologicas*
*Projeto: Tozi Imoveis — IA de Atendimento + Processos Internos*
*Inicio: 16/03/2026 | Fim Ciclo 1: 13/03/2027 | Contrato: 36 meses*
