# Tozi SDR - Sistema de Atendimento Inteligente

**Documento Executivo**
**Cliente:** Tozi Imobiliária (Sinop/MT)
**Versão:** 1.0 | Fevereiro 2026

---

## O que é

Sistema de atendimento automatizado para WhatsApp que combina inteligência artificial com atendimento humano. O objetivo é **agilizar o primeiro contato** com o cliente, coletar informações relevantes e preparar o terreno para o time de vendas.

O sistema não substitui o atendente — ele **prepara e enriquece** o atendimento.

---

## Como funciona

```
Cliente manda mensagem no WhatsApp
        ↓
    [ Clara ]  ←  Recepciona, conversa, entende a demanda
        ↓
  Coleta informações básicas
        ↓
    Confirma o nome do cliente
        ↓
  Busca imóveis relevantes (se aplicável)
        ↓
    Passa para Camila com dossiê completo
        ↓
 Camila recebe: resumo + sugestão de imóveis
        ↓
  Atendimento humano continua
```

---

## Os Agentes

### Clara — A Recepcionista Virtual

Clara é a primeira pessoa que o cliente "conversa" no WhatsApp. Ela faz o pré-atendimento.

#### O que a Clara FAZ

| Função | Descrição |
|--------|-----------|
| **Acolhe** | Responde saudações de forma natural e simpática |
| **Esclarece** | Responde dúvidas simples sobre a empresa (horário, endereço, serviços) |
| **Qualifica** | Coleta informações sobre o que o cliente procura |
| **Confirma** | Verifica o nome real do cliente antes de encaminhar |
| **Encaminha** | Passa o atendimento para o time com todas as informações organizadas |

#### O que a Clara NÃO FAZ

- Não busca imóveis diretamente para o cliente
- Não agenda visitas
- Não negocia valores
- Não resolve problemas de boleto, contrato ou manutenção
- Não promete prazos
- Não pede documentos ou dados sensíveis

#### Como a Clara se comporta

**Humana e natural:**
- Respostas curtas (1-3 frases)
- Uma pergunta por vez
- Sem formalidade forçada
- Adapta o tom ao cliente
- Emoji só quando faz sentido (máximo 1)

**Exemplo de conversa:**

```
Cliente: Oi, boa tarde!
Clara: Oi! Tudo bem? Como posso te ajudar?

Cliente: Quero ver umas casas pra alugar
Clara: Ótimo! Casa pra alugar em Sinop mesmo?

Cliente: Sim, no centro
Clara: Beleza! Tem ideia de quanto quer pagar de aluguel?

Cliente: Até uns 2 mil
Clara: Perfeito. E quantos quartos precisa?

Cliente: 3 quartos, tenho dois filhos
Clara: Entendi! Só pra confirmar, qual seu nome completo?

Cliente: João da Silva
Clara: Obrigada, João! Vou passar pro nosso time, já já te chamam!
```

#### Dois modos de operação

| Horário | Comportamento |
|---------|---------------|
| **Dentro do expediente** | Ágil. Entende o básico, confirma nome e passa pro time. |
| **Fora do expediente** | Mais calmo. Qualifica o lead com mais profundidade, monta dossiê rico. |

**Horário comercial Tozi:**
- Segunda a Sexta: 7:30-11:30 e 13:30-17:30
- Sábado: 9:00-11:30
- Domingo: Fechado

---

### Atribuidor — O Bastidor da Clara

O Atribuidor trabalha nos bastidores. O cliente nunca vê. Ele é acionado quando a Clara termina a conversa inicial.

#### O que ele faz

1. **Analisa** o que a Clara coletou
2. **Busca imóveis** se há critérios suficientes (tipo, valor, região)
3. **Monta o resumo** do atendimento
4. **Sugere imóveis** com links do site (quando encontra)
5. **Passa para Camila** com tudo organizado

#### Exemplo de entrega para Camila

**Resumo (mensagem privada):**
```
📋 Pré-Atendimento

Cliente: João da Silva
Demanda: Locação
Detalhes: Procura casa de 3 quartos no centro de Sinop,
orçamento até R$ 2.000/mês. Tem dois filhos.
```

**Sugestão (mensagem privada):**
```
🔍 Imóveis encontrados

5 casas para alugar no centro até R$ 2.000:

• Cód. 9561 — Casa 3 quartos, Jardim Ouro, R$ 1.800/mês
  https://www.toziimoveis.com.br/casa-jardim-ouro-sinop,9561

• Cód. 9445 — Casa 3 quartos, Centro, R$ 2.000/mês
  https://www.toziimoveis.com.br/casa-centro-sinop,9445

...
```

---

### Copiloto — O Assistente do Time

O Copiloto ajuda os atendentes durante o atendimento. Ele é acionado **sob demanda** quando alguém do time precisa de ajuda.

#### Como acionar

O atendente envia uma mensagem **privada** com `#tozi` seguido da pergunta:

```
#tozi quais imóveis temos perto da unifasipe?
```

O Copiloto responde em privado. O cliente não vê nada.

#### O que o Copiloto faz

| Função | Exemplo |
|--------|---------|
| **Busca imóveis** | "Quais casas temos no Jardim Paraíso até 3 mil?" |
| **Localiza cliente** | "Qual o contrato do João Silva?" |
| **Consulta processos** | "Quais documentos pra renovar contrato?" |
| **Responde dúvidas** | "Qual a taxa de administração da Tozi?" |

#### Comportamento do Copiloto

- **Direto e rápido** — O atendente está ocupado, precisa de resposta objetiva
- **Não faz perguntas** — Busca a informação ou diz o que precisa
- **Invisível pro cliente** — Tudo acontece em mensagens privadas

---

## Tipos de Atendimento

### Comercial (Locação, Venda, Captação)

**O que a Clara coleta:**
- O que procura (casa, apartamento, terreno, kitnet, sala comercial)
- Finalidade (alugar, comprar, anunciar imóvel próprio)
- Região ou bairro preferido
- Faixa de valor
- Quantidade de quartos
- Se tem pets
- Prazo (urgente, sem pressa)

**O que o Atribuidor busca:**
- Imóveis que correspondem aos critérios
- Links do site da Tozi para cada opção

### Suporte (Boleto, Contrato, Manutenção)

**O que a Clara coleta:**
- Qual o problema
- Endereço do imóvel (se mencionado)
- Nome do cliente

**O que o Atribuidor faz:**
- Busca cadastro do cliente na base
- Monta resumo curto e passa pro time

### Dúvidas sobre a Empresa

A Clara consulta a base de conhecimento (FAQ) e responde diretamente. Se não tiver a resposta, avisa que o time pode confirmar.

---

## Fluxo Visual

```
┌─────────────────────────────────────────────────────────────────────┐
│                         CLIENTE NO WHATSAPP                         │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                              CLARA                                  │
│                                                                     │
│  "Oi! Como posso te ajudar?"                                       │
│  "Casa pra alugar em Sinop mesmo?"                                 │
│  "Quantos quartos precisa?"                                        │
│  "Qual seu nome completo?"                                         │
│  "Vou passar pro time!"                                            │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                           ATRIBUIDOR                                │
│                         (nos bastidores)                            │
│                                                                     │
│  → Analisa informações coletadas                                   │
│  → Busca imóveis compatíveis                                       │
│  → Monta resumo + sugestão                                         │
│  → Passa pra Camila                                                │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                             CAMILA                                  │
│                       (atendente humana)                            │
│                                                                     │
│  Recebe:                                                           │
│  📋 Resumo do pré-atendimento                                      │
│  🔍 Sugestão de imóveis com links                                  │
│                                                                     │
│  → Continua o atendimento com contexto completo                    │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                            COPILOTO                                 │
│                      (assistente sob demanda)                       │
│                                                                     │
│  Camila: "#tozi quais imóveis perto da unifasipe?"                 │
│  Copiloto: "Encontrei 3 casas próximas: ..."                       │
│                                                                     │
│  (responde em privado, cliente não vê)                             │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Benefícios do Sistema

| Para o Cliente | Para o Time |
|----------------|-------------|
| Atendimento imediato 24/7 | Recebe lead qualificado, não cru |
| Não precisa repetir informações | Sugestão de imóveis já pronta |
| Conversa natural, não menu de opções | Histórico organizado |
| Sabe que será atendido por humano | Copiloto ajuda durante atendimento |

---

## Limites e Regras

### O que o sistema NUNCA faz

1. **Não negocia** — Apenas coleta informações e passa pro time
2. **Não promete** — Não diz "temos o imóvel perfeito", apenas passa opções
3. **Não resolve suporte** — Coleta o problema e encaminha
4. **Não pede documentos** — Segurança de dados
5. **Não inventa** — Se não sabe, diz que o time confirma

### Quando o sistema passa pro time

- Assim que entender o que o cliente precisa
- Depois de confirmar o nome real do cliente
- Quando o cliente pede pra falar com atendente
- Quando não consegue responder uma pergunta

---

## Roadmap Futuro

| Item | Descrição | Prioridade |
|------|-----------|------------|
| **Consulta de cadastro** | Buscar dados de inquilinos/proprietários | Alta |
| **Avaliação de qualidade** | Medir se a Clara está atendendo bem | Alta |
| **Follow-up automático** | Reativar clientes que não responderam | Média |
| **Perguntar aos gerentes** | Copiloto consulta grupo de gestores quando não sabe | Média |
| **Portal de FAQ** | Interface para gerentes atualizarem a base de conhecimento | Média |

---

## Contato

**Desenvolvido por:** Midwest Engenharia
**Suporte técnico:** Paulo Seze

---

*Este documento é uma versão executiva para stakeholders. A documentação técnica completa está disponível na pasta do projeto.*
