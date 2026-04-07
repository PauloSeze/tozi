"""Client HTTP para a API do SPX (ChatWoot)."""

from __future__ import annotations

import logging

import httpx

from config import SPX_ACCOUNT_ID, SPX_BASE_URL, SPX_BOT_TOKEN

logger = logging.getLogger(__name__)

_BASE = f"{SPX_BASE_URL}/api/v1/accounts/{SPX_ACCOUNT_ID}"
_HEADERS = {
    "api_access_token": SPX_BOT_TOKEN,
    "Content-Type": "application/json",
}


async def enviar_mensagem(conversa_id: int, texto: str, private: bool = False) -> dict:
    """Envia uma mensagem (pública ou privada) na conversa."""
    url = f"{_BASE}/conversations/{conversa_id}/messages"
    payload = {
        "content": texto,
        "message_type": "outgoing",
        "private": private,
        "content_type": "text",
    }
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.post(url, json=payload, headers=_HEADERS)
        resp.raise_for_status()
        logger.info("conversa=%s mensagem enviada (private=%s)", conversa_id, private)
        return resp.json()


async def marcar_atendimento(conversa_id: int, ativo: bool) -> None:
    """Atualiza custom_attributes.atendimento na conversa."""
    url = f"{_BASE}/conversations/{conversa_id}"
    payload = {"custom_attributes": {"atendimento": ativo}}
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.patch(url, json=payload, headers=_HEADERS)
        resp.raise_for_status()
        logger.info("conversa=%s atendimento=%s", conversa_id, ativo)
