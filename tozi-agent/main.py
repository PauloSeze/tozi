"""
Tozi Agent — Servidor principal.

Recebe webhooks do SPX (ChatWoot), normaliza e roteia.
"""

from __future__ import annotations

import logging
import traceback

from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

import memoria
import spx
from agentes.clara import processar as clara_processar
from config import deve_processar
from normalizar import Evento, determinar_rota, normalizar

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)
logger = logging.getLogger("tozi")

app = FastAPI(title="Tozi Agent", version="0.1.0")


@app.post("/webhook/spx")
async def webhook_spx(request: Request) -> JSONResponse:
    try:
        body: dict = await request.json()
        evento: Evento = normalizar(body)

        if not deve_processar(evento.conversa_id):
            return JSONResponse({"status": "skipped"})

        rota = determinar_rota(evento)
        logger.info("conversa=%s rota=%s sender=%s", evento.conversa_id, rota, evento.sender_type)

        if rota == "ignorar":
            return JSONResponse({"status": "ignored"})

        if rota == "agente_clara":
            historico = await memoria.carregar(evento.conversa_id)
            resposta, historico = await clara_processar(evento, historico)
            await spx.enviar_mensagem(evento.conversa_id, resposta)
            await memoria.salvar(evento.conversa_id, historico)

        elif rota == "marcar_atendimento":
            await spx.marcar_atendimento(evento.conversa_id, True)

        elif rota == "limpar_atendimento":
            await spx.marcar_atendimento(evento.conversa_id, False)
            await memoria.limpar(evento.conversa_id)

        elif rota == "copiloto":
            logger.info("conversa=%s -> copiloto (pendente implementação)", evento.conversa_id)

        return JSONResponse({"status": "ok", "rota": rota})

    except Exception:
        logger.error("Erro no webhook: %s", traceback.format_exc())
        return JSONResponse({"status": "error"})


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}
