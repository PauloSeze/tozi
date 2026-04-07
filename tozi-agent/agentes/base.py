"""Loop de agente genérico usando Anthropic SDK."""

from __future__ import annotations

import logging
from typing import Any, Callable, Awaitable

import anthropic

from config import ANTHROPIC_API_KEY

logger = logging.getLogger(__name__)

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

ToolHandler = Callable[[str, dict], Awaitable[Any]]


async def executar_agente(
    system: str,
    historico: list[dict],
    tools: list[dict] | None = None,
    tool_handler: ToolHandler | None = None,
    model: str = "claude-sonnet-4-6",
    max_tokens: int = 1024,
) -> tuple[str, list[dict]]:
    """Executa o loop de agente até end_turn ou erro."""

    kwargs: dict[str, Any] = {
        "model": model,
        "system": system,
        "messages": historico,
        "max_tokens": max_tokens,
    }
    if tools:
        kwargs["tools"] = tools

    while True:
        resposta = client.messages.create(**kwargs)
        historico.append({"role": "assistant", "content": _serializar_content(resposta.content)})

        if resposta.stop_reason == "end_turn":
            texto = next((b.text for b in resposta.content if b.type == "text"), "")
            return texto, historico

        if resposta.stop_reason == "tool_use" and tool_handler:
            resultados = []
            for bloco in resposta.content:
                if bloco.type == "tool_use":
                    resultado = await tool_handler(bloco.name, bloco.input)
                    resultados.append({
                        "type": "tool_result",
                        "tool_use_id": bloco.id,
                        "content": str(resultado),
                    })
            historico.append({"role": "user", "content": resultados})
            kwargs["messages"] = historico
            continue

        break

    return "Não consegui processar no momento.", historico


def _serializar_content(content: list) -> list[dict]:
    """Converte content blocks da API para dicts serializáveis."""
    resultado = []
    for bloco in content:
        if bloco.type == "text":
            resultado.append({"type": "text", "text": bloco.text})
        elif bloco.type == "tool_use":
            resultado.append({
                "type": "tool_use",
                "id": bloco.id,
                "name": bloco.name,
                "input": bloco.input,
            })
    return resultado
