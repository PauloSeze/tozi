# Vision — Análise de Imagem

**Node:** OpenAI (Vision)
**Modelo:** GPT-4o-mini
**Operação:** Analyze Image

---

## Prompt de Análise

Analise a imagem e retorne uma descrição objetiva e concisa em português.

Identifique e informe:

**TIPO DE IMAGEM:** foto de fachada, foto de cômodo, foto de planta/terreno, foto de documento, print de tela, foto de placa, mapa/localização, foto pessoal, outro.

**IMÓVEL (se identificável):**
- Tipo: casa, apartamento, sobrado, kitnet, barracão, sala comercial, terreno, fazenda, outro
- Características visíveis: número de pavimentos, garagem, piscina, estado de conservação, acabamento
- Cômodo (se interno): sala, quarto, cozinha, banheiro, área de serviço, varanda, outro

**PLACA (se visível):**
- Existe placa de venda, aluguel, aluga-se ou vende-se? SIM ou NÃO
- Se SIM: tipo (venda ou aluguel) e código numérico se legível

**TEXTO NA IMAGEM (se houver):** transcreva qualquer texto legível relevante — valores, telefones, códigos, endereços.

**DESCRIÇÃO GERAL:** em 1-2 frases, descreva o que a imagem mostra de forma útil para um atendente imobiliário.

Seja direto. Não invente informações que não são visíveis na imagem.

---

## Input

```
{{ $json.midia.url }}
```

URL da imagem vinda do attachment do webhook.

---

## Output

Texto livre com a análise estruturada da imagem.

---

## Uso no Fluxo

1. Imagem chega via webhook
2. Roteada para processamento de mídia
3. Vision analisa a imagem
4. Resultado formatado pelo node "Formatar Mídia"
5. Enviado como nota privada no ChatWoot
6. Segue para a rota final (Clara ou Marcar)
