# Runbook — demo Tozi (IA de vendas + follow-up no front)

Estado em 2026-05-19 (noite). Foco da demo: **IA de vendas funcionando** + **follow-up visível no front**. Lead do Meta fica pra depois (Paulo resolve à parte).

## ✅ Já verificado (servidor estava na rede)

- **Triagem → vendas funciona**: playground com "quero comprar casa até 300 mil financiada" → roteia pro `scenario_1_vendas_agent` (Júlia), responde em 1ª pessoa ("aqui na Tozi"), oferece financiamento e qualifica antes de buscar.
- Modelo `gpt-5-mini`, chaves OpenAI+Anthropic presentes.
- 3 scenarios enabled (Vendas/Locação com tools Vista, Suporte sem).
- Copilot do gerente com `get_conversation_analysis` (eval) — gateado por `report_manage`.

## ⚠️ Verificar ANTES da reunião (precisa estar na rede da PAULAO)

### 1. RISCO #1 — busca Vista de VENDA retorna imóveis de verdade?
O payload da tool trata venda (`%25vend%25` + `ValorVenda`), mas o Vista retorna **hash de chaves numéricas** (não array) — e o `response_template` committado itera como array. Confirmar se a tool LIVE já está com `response_template` vazio (gotcha #16) e se a busca real volta listagem.

```bash
# na rede:
ssh paulo@192.168.8.100   # senha master123
# checar template live:
sudo -u chatwoot bash -lc 'cd /home/chatwoot/chatwoot && RAILS_ENV=production bundle exec rails runner "t=Account.find(1).captain_custom_tools.find_by(slug:%q(custom_buscar_imoveis_no_vista)); puts t.response_template.to_s.strip.empty? ? %q(VAZIO-ok) : %q(TEM-TEMPLATE-revisar)"'
# teste real de busca (single-turn força tool):
curl -sS --max-time 110 -X POST http://localhost:3000/api/v1/accounts/1/captain/assistants/1/playground \
  -H 'api_access_token: sxLWdXeSwLpNMBcG5FKMdRA6' -H 'Content-Type: application/json' \
  -d '{"assistant":{"message_content":"Pode me mostrar agora as casas a venda ate 300 mil em Sinop com codigo e link"}}'
```
Se voltar listagem com códigos/links → ✅ demo de vendas redonda. Se voltar "nenhum imóvel" mesmo havendo → setar `response_template` vazio na tool e reusar.

### 2. Teste E2E real (WhatsApp do Paulo) — o mais convincente pra demo
Mandar no WhatsApp do número fixado (+5566996247866) algo como:
"Oi, quero comprar uma casa em Sinop até 350 mil, pode ser financiada" → esperar Clara → Júlia qualificar → pedir pra ver opções → confirmar que busca Vista e escala pra humano. Esse é o roteiro da reunião.

## 🆕 Follow-up no front — aplicar (1 vez, na rede)

```bash
# 1. atualizar o engine na PAULAO com as mudanças de label (commit tozi d09636c)
#    se /home/paulo/tozi-followup é git clone: git pull
#    senão, copiar engine/engine.py, engine/spx.py e setup_spx_front.py
# 2. criar as definições de custom attribute + labels no chatwoot:
cd /home/paulo/tozi-followup && .venv/bin/python setup_spx_front.py
```
Depois disso, toda conversa que o engine tocar mostra no **sidebar do chatwoot**: `tozi_status_lead`, `tozi_fonte`, `tozi_followup_attempts`, `tozi_last_followup_day` — e aparece nos folders de label `lead-novo` / `followup-ativo` / `lead-esfriado`.

### Pra MOSTRAR follow-up na reunião sem esperar lead real
Semear a conversa de teste com estado de follow-up (depois de rodar o setup acima):
```bash
curl -sS -X POST http://localhost:3000/api/v1/accounts/1/conversations/<CONV_ID>/custom_attributes \
  -H 'api_access_token: sxLWdXeSwLpNMBcG5FKMdRA6' -H 'Content-Type: application/json' \
  -d '{"custom_attributes":{"tozi_status_lead":"em_contato","tozi_fonte":"META_ADS","tozi_followup_attempts":2,"tozi_last_followup_day":3}}'
# + aplicar label followup-ativo
curl -sS -X POST http://localhost:3000/api/v1/accounts/1/conversations/<CONV_ID>/labels \
  -H 'api_access_token: sxLWdXeSwLpNMBcG5FKMdRA6' -H 'Content-Type: application/json' \
  -d '{"labels":["followup-ativo"]}'
```
Abrir a conversa no chatwoot → sidebar mostra o rastreio de follow-up; folder `followup-ativo` lista ela.

## Gaps conhecidos (não bloqueiam a demo)
- Lead Meta → SPX direto (#15): Paulo resolve à parte.
- Dossiê rico no handoff (#20): hoje é `handoff_message` simples.
- BDR (reativação 90d): stub, depende de campo Vista.
