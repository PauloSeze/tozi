# Relatório de Análise Comportamental — IA Tozi

**Para:** Diretoria e Gerência da Tozi Imóveis
**De:** SimplexIA (SPXIA)
**Data:** 27/03/2026
**Assunto:** Análise do comportamento da IA no atendimento aos clientes — problemas identificados e pontos de melhoria

---

## Objetivo

Analisamos conversas reais da IA (Clara) com clientes em ambos os canais de atendimento:

- **Telefone Fixo (comercial)** — busca de imóveis, locação, venda
- **Prestação de Serviços (suporte)** — manutenção, boletos, contratos, desocupação

O objetivo é identificar onde a IA está ajudando, onde está atrapalhando, e o que precisa mudar.

---

## O que está funcionando bem

A Clara tem pontos positivos que valem destaque:

- **Acolhimento natural** — a primeira impressão é boa, os clientes interagem sem estranhamento
- **Coleta de informações** — em muitos casos, a IA consegue entender o que o cliente precisa e organiza um resumo útil para o time
- **Resumo interno** — as notas privadas que a Clara gera para os consultores contêm informações ricas (nome, o que procura, preferências, faixa de valor)
- **Suporte simples** — em casos diretos (ex: boleto não chegou), a IA coleta o problema e encaminha rápido

---

## Problemas que identificamos

### 1. A IA toma partido do cliente contra a imobiliária

**Este é o problema mais sério e que gerou queixa da equipe.**

Em conversas de suporte onde o cliente está insatisfeito, a Clara se posiciona como aliada do cliente, validando reclamações e prometendo cobranças que ela não tem como cumprir.

**Exemplo real — cliente com manutenção atrasada há 3 meses:**

> **Cliente:** "já faz 3 meses, isso é um absurdo, eu já arrumei tudo por conta, falta de respeito"
>
> **Clara:** "Você tem razão, Rafael… realmente já passou tempo demais. Vou cobrar **prioridade máxima** e pedir **retorno imediato**."

O que está errado aqui:
- A IA **deu razão ao cliente** dizendo "você tem razão" e "você não deveria ter resolvido por conta"
- **Prometeu coisas que não pode cumprir**: "prioridade máxima", "retorno imediato", "vou acompanhar até resolver"
- **Deu a entender que estava cobrando o time** — o cliente passa a achar que a equipe está sendo negligente e que até a IA reconhece isso
- Quando o time humano assume, o cliente já chega com expectativa inflada e revoltado

**O correto seria:** A IA ser empática ("entendi sua situação") sem dar opinião sobre quem tem razão, e encaminhar para o setor responsável sem prometer prazos.

---

### 2. A IA não mostra imóveis quando o cliente pede

No atendimento comercial, quando o cliente pergunta "o que vocês têm?", a IA não consegue mostrar opções. Ela fica fazendo perguntas de qualificação sem nunca entregar nada concreto.

**Exemplo real:**

> **Cliente:** "me passe o que vocês tem" *(3 vezes)*
>
> **Clara:** "Tem alguma preferência de quartos?"... "Qual faixa de valor?"... "Algum bairro?"

O cliente vai ficando frustrado porque quer ver imóveis e a IA só faz perguntas. Isso aconteceu em várias conversas. Estamos trabalhando para que a IA consiga buscar e mostrar imóveis diretamente durante a conversa.

---

### 3. A IA responde pesquisas de NPS como se fossem mensagens reais

Quando uma conversa é encerrada, o sistema envia a pesquisa de satisfação ("De 0 a 10, qual nota você dá?"). O problema: quando o cliente responde com texto junto da nota, a IA interpreta como uma nova conversa.

**Exemplo real:**

> **Sistema:** "De 0 a 10, qual é a nota?"
>
> **Cliente:** "8, se fazer presente valoriza o empreendimento"
>
> **Clara:** "Oi! Parece que você está pensando em valorizar um empreendimento. Quer algumas dicas?"

A IA transformou uma resposta de NPS em um atendimento comercial. Isso confunde o cliente e gera trabalho desnecessário para o time.

---

### 4. A IA ignora quando o cliente quer falar com uma pessoa

Em pelo menos uma conversa, a cliente pediu **3 vezes** "quero falar com atendente por gentileza" e a IA continuou respondendo automaticamente sem transferir.

Isso precisa ser uma regra absoluta: se o cliente pedir atendente humano, transferir imediatamente.

---

### 5. A IA confunde pessoas mencionadas pelo cliente com funcionários

**Exemplo reportado:** Uma cliente disse que esteve na empresa com a "Tatiele" (cônjuge, titular de contrato). A IA entendeu que Tatiele era uma funcionária e disse que atribuiria o atendimento a ela.

A IA não conhece o quadro de funcionários da Tozi, então não sabe diferenciar. Estamos criando uma ferramenta para que ela consulte a lista de colaboradores.

---

### 6. Qualificação demorada quando o time está disponível

Dentro do horário comercial, a IA deveria ser mais ágil: entender o que o cliente precisa e passar para o consultor rapidamente. Em várias conversas, a IA ficou fazendo perguntas extras mesmo quando já tinha informação suficiente.

**Exemplo real:**

> A cliente informou: apartamento + região do Hospital Santo Antônio + Edifício Florença + até R$ 2.800
>
> A IA ainda perguntou: "Qual seria seu orçamento?" e "Tem algum bairro de preferência?"
>
> *(ambas informações já tinham sido dadas)*

---

### 7. A IA usa muitos emojis

Quase toda despedida tem 😊, 😉 ou 🥰. Embora não seja um problema grave, soa artificial e repetitivo. A IA deveria usar emoji com mais parcimônia.

---

## O que já estamos providenciando

| Ação | Status |
|------|--------|
| Corrigir filtro de NPS para não acionar a IA | Planejado |
| Ajustar tom da IA no suporte (empática mas neutra, sem tomar partido) | Planejado |
| Criar regra de transferência imediata quando cliente pedir atendente | Planejado |
| Permitir que a IA mostre imóveis durante a conversa | Planejado |
| Criar consulta à lista de colaboradores | Planejado |
| Atualizar base de conhecimento com as respostas do questionário | Planejado |
| Criar ferramenta para atualizar nome do contato quando confirmado | Planejado |

---

## Pedimos a colaboração de vocês

Gostaríamos de saber:

1. **Vocês identificam outros comportamentos problemáticos da IA que não foram mencionados aqui?**

2. **Sobre o tom no suporte:** qual seria o tom ideal que a IA deveria ter quando o cliente reclama? Algum exemplo de como vocês gostariam que ela respondesse?

3. **Sobre a venda de imóveis:** ainda não recebemos as informações sobre como funciona a venda na Tozi (financiamento, FGTS, documentação, corretagem). Precisamos disso para a base de conhecimento.

4. **Algum outro tipo de informação que os clientes costumam perguntar e que a IA deveria saber responder?**

5. **Sobre a distribuição de atendimentos:** hoje a IA sempre encaminha para a mesma pessoa (Camila). Gostariam de um rodízio entre consultores? Se sim, quais são as regras?

---

*Qualquer dúvida, estamos à disposição.*

**SimplexIA — Inteligência Artificial para Negócios**
Sinop/MT
