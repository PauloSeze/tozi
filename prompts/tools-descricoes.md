# Tools — Descrições para os Agentes

Descrições usadas nos nodes toolWorkflow e vectorStoreInMemory para orientar o uso das tools pelos agentes.

---

## buscar_imoveis

**Tipo:** toolWorkflow
**Workflow:** Tozi TOOL - Buscar imóveis (`ZvrUozDnbEzRZfFs`)

### Descrição

Busca imóveis no Vista com filtros progressivos. Retorna JSON com lista de imóveis.

**ESTRUTURA OBRIGATÓRIA:**
```json
{
  "filter": {},      // Filtros AND
  "advFilter": {},   // Filtros complexos OR/AND
  "order": {},       // Ordenação
  "paginacao": {}    // Limite de resultados
}
```

**FILTER (condições AND):**
- Codigo: "0001"
- Cidade: "Sinop" (padrão, pode omitir)
- Categoria: "Casa" | "Apartamento" | "Comercial" | "Terreno"
- Status: ["like", "%alug%"] (SEMPRE incluir para locação)
- ValorLocacao: ["min", "max"] ou ["", max] ou [min, ""]
- Dormitorios: numero ou [min, max]
- Suites: numero ou [min, max]
- Vagas: numero ou [min, max]
- Bairro: "Nome do Bairro"
- AreaPrivativa: [min, max] em m²
- AreaTotal: [min, max] em m²
- Latitude: [lat_min, lat_max] (quando usar buscar_localizacao)
- Longitude: [lng_min, lng_max] (quando usar buscar_localizacao)

**ADVFILTER (condições complexas):**

Para múltiplas opções de um campo:
```json
{
  "Or": {
    "Bairro": "Centro",
    "Or": {
      "Bairro": "Jardim Botânico"
    }
  }
}
```

Para busca textual:
```json
{
  "Endereco": ["like", "%Nome da Rua%"],
  "CaracteristicaComplementar": ["like", "%piscina%"]
}
```

**ORDER:**
- "Codigo": "desc" (mais recentes)
- "ValorLocacao": "asc" (mais baratos primeiro)
- Combine múltiplas ordenações

**PAGINACAO:**
- pagina: 1, 2, 3...
- quantidade: 5 (recomendado), max 20

**ESTRATÉGIA DE BUSCA:**
1. Se houver referência geográfica, use buscar_localizacao primeiro
2. Comece amplo: apenas cidade e tipo
3. Refine por valor se muitos resultados
4. Adicione bairros se conhecer preferência
5. Use características apenas se essencial

---

## buscar_localizacao

**Tipo:** toolWorkflow
**Workflow:** Tozi TOOL - Buscar Localização (`dTUGxaH5AwEDFen0`)

### Descrição

Converte referência geográfica em coordenadas para filtro de proximidade.

Sempre complete o input com "sinop mt" se não especificado.

**INPUT:** texto com referência geográfica
- "fasipe sinop mt"
- "unic campus sinop mt"
- "shopping sinop mt"
- "hospital regional sinop mt"

**OUTPUT:** coordenadas para o campo filter do buscar_imoveis
```json
[{
  "Latitude": ["-11.806...", "-11.896..."],
  "Longitude": ["-55.491...", "-55.583..."]
}]
```

**QUANDO USAR:**
- Clara mencionou referência geográfica ("perto de", "próximo a", "região do")
- Antes de buscar_imoveis com filtro de localização

**QUANDO NÃO USAR:**
- Cliente informou bairro específico (use direto no filter)
- Não há referência geográfica

---

## atribuir_atendimento

**Tipo:** toolWorkflow
**Workflow:** Tozi TOOL - Atribuir Atendimento (`PTHEJTw8ZWkgXt7F`)

### Descrição

Atribui a conversa para a Camila. Envia resumo como mensagem privada e sugestão como mensagem privada separada (se fornecida).

**INPUT:**
```json
{
  "resumo": "texto do resumo",
  "sugestao": "texto da sugestão ou string vazia se não houver"
}
```

A tool internamente:
1. Envia resumo como mensagem privada
2. Envia sugestão como mensagem privada separada (se não for vazia)
3. Atribui a conversa para a Camila

**QUANDO USAR:**
- Sempre por último, depois de todas as buscas

**QUANDO NÃO USAR:**
- Se ainda está fazendo buscas

---

## faq_tozi

**Tipo:** vectorStoreInMemory (retrieve-as-tool)
**Modelo de Embeddings:** OpenAI

### Descrição

Consulta a base de conhecimento da Tozi Imobiliária.

Contém: horários de funcionamento, endereço, telefone, serviços oferecidos, documentação necessária para locação e venda, regras sobre fiador, pets, reformas, processos de desocupação, renovação de contrato, e perguntas frequentes.

**QUANDO USAR:**
- Cliente perguntou algo sobre a empresa ou seus processos
- Você não tem certeza de uma informação
- Dúvidas sobre documentação, regras ou procedimentos

**QUANDO NÃO USAR:**
- Informações que já estão no seu prompt (horário, endereço, telefone)
- Perguntas que não são sobre a Tozi

---

## consultar_cadastro

**Tipo:** toolWorkflow (pendente implementação)

### Descrição

Busca cliente na base pelo nome. Use para localizar inquilinos ou proprietários.

**Status:** Endpoint Vista ainda não definido.

---

## Think (toolThink)

**Tipo:** toolThink
**Disponível para:** Clara, Copiloto

### Descrição

Tool de raciocínio interno. Permite ao agente "pensar" antes de responder, organizando informações e planejando a resposta.

Usado automaticamente pelo framework de agentes quando necessário.
