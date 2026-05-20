# Tozi Follow-up & Prospecção Engine

Engine Python que dispara mensagens proativas pra leads Tozi:

1. **SDR Passivo** — Polling Vista CRM a cada 5min. Detecta lead novo no bucket "Tozi Imóveis Lead" (ID 20) e dispara primeira mensagem via SPX (Captain assume com Clara).
2. **Follow-up** — Cron diário 09:00 MT. Reabordagem em D+1 / D+3 / D+7 / D+14 / D+30 / D+60 / D+90 para conversas sem resposta. Máx 4 tentativas por lead antes de marcar como morto.
3. **BDR** — Cron semanal. Varredura de leads na base com última interação > 90 dias.

Não substitui a Clara/Júlia/Bruna/Letícia. É o **disparador** — quem conversa depois é o time de agentes do Captain dentro do SPX.

## Arquitetura

```
┌──────────────┐    poll 5min     ┌──────────────┐
│ Vista (Loft) │ ◄─────────────── │ engine.py    │ ── cria contact+conv ──► ┌──────┐
│ /clientes    │                  │              │     via SPX API          │ SPX  │
└──────────────┘                  └──────┬───────┘                          │      │
                                         │                                  │ ──► WhatsApp via WAHA
                                         │ cron diário                      │      ◄── resposta
                                         ▼                                  │      ── Captain processa
                                  follow-up D+N                             │      ── Clara/Júlia/Bruna assumem
                                  via SPX API                               └──────┘
```

A mensagem inicial vai como `Channel::Api` → webhook outgoing → WAHA → WhatsApp. Resposta do cliente cria mensagem incoming no SPX → router whitelist deixa passar (se o número do cliente bater) → Captain (Clara) processa.

## Setup

```bash
cd tozi/follow_up_engine
python -m venv .venv
.venv\Scripts\activate    # Windows
pip install -r requirements.txt
cp .env.example .env
# editar .env com credenciais reais
```

## Uso

```bash
# Smoke test: lista leads novos no Vista sem disparar nada
python -m engine poll --dry-run

# Disparar de verdade
python -m engine poll

# Follow-up diário (cron 09:00 MT)
python -m engine followup

# BDR varredura semanal
python -m engine bdr

# Disparar mensagem manual (debug)
python -m engine send +5566996247866 "Oi! Mensagem de teste."
```

## Deploy (futuro)

**Opção A — Coolify VPS (Boston, junto com agents-runtime)**

1. Push pra repo separado `PauloSeze/tozi-followup-engine`
2. Novo app no Coolify apontando pra esse repo
3. Variáveis de ambiente: copiar de `.env`
4. Scheduled tasks (Coolify): `python -m engine poll` a cada 5min, `python -m engine followup` diário 09:00, `python -m engine bdr` semanal segunda 09:00

**Opção B — Reusar n8n da Tozi**

Criar 3 workflows scheduled: poll/followup/bdr. Cada workflow chama esta API (transformar engine em FastAPI HTTP) ou roda o script diretamente em Code Node.

## Estado atual

- ✅ Polling Vista (detecção de leads novos)
- ✅ Disparo via SPX API (Channel::Api / inbox 1)
- ✅ Templates de primeira mensagem por fonte (Meta Ads, Site, Instagram)
- ✅ Follow-up D+1/3/7/14/30/60/90 (configurável)
- ✅ BDR varredura > 90 dias
- ✅ Deduplicação (não dispara pra quem já tem conversa aberta)
- ⏳ Tracking de tentativas via SPX custom_attributes (precisa testar em produção)
- ⏳ Deploy

## Variáveis de ambiente

Ver `.env.example` — Vista, SPX, número remetente, configs de cadência.
