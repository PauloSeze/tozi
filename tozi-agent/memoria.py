"""Memória de conversas — Redis com fallback em memória local."""

from __future__ import annotations

import json
import logging

from config import REDIS_URL

logger = logging.getLogger(__name__)

JANELA = 40
TTL_SEGUNDOS = 86400  # 24h

# Fallback em memória (para dev sem Redis)
_local: dict[str, list[dict]] = {}
_usar_redis: bool | None = None


def _chave(conversa_id: int) -> str:
    return f"historico:{conversa_id}"


async def _get_redis():
    global _usar_redis
    if _usar_redis is False:
        return None
    try:
        import redis.asyncio as aioredis
        r = aioredis.from_url(REDIS_URL, decode_responses=True)
        await r.ping()
        _usar_redis = True
        return r
    except Exception:
        if _usar_redis is None:
            logger.warning("Redis indisponível — usando memória local (dados perdem ao reiniciar)")
        _usar_redis = False
        return None


async def carregar(conversa_id: int) -> list[dict]:
    """Carrega as últimas JANELA mensagens da conversa."""
    r = await _get_redis()
    if r:
        try:
            raw = await r.get(_chave(conversa_id))
            if not raw:
                return []
            return json.loads(raw)[-JANELA:]
        finally:
            await r.aclose()
    else:
        return list(_local.get(_chave(conversa_id), []))[-JANELA:]


async def salvar(conversa_id: int, mensagens: list[dict]) -> None:
    """Salva o histórico (truncado na janela)."""
    truncado = mensagens[-JANELA:]
    r = await _get_redis()
    if r:
        try:
            await r.set(_chave(conversa_id), json.dumps(truncado, ensure_ascii=False), ex=TTL_SEGUNDOS)
        finally:
            await r.aclose()
    else:
        _local[_chave(conversa_id)] = truncado
    logger.info("conversa=%s memória salva (%d msgs)", conversa_id, len(truncado))


async def limpar(conversa_id: int) -> None:
    """Remove o histórico da conversa."""
    r = await _get_redis()
    if r:
        try:
            await r.delete(_chave(conversa_id))
        finally:
            await r.aclose()
    else:
        _local.pop(_chave(conversa_id), None)
    logger.info("conversa=%s memória limpa", conversa_id)
