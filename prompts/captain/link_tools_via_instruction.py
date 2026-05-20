"""Anexa references markdown de tools no instruction dos Scenarios pra vincular as tools.

O Captain::Scenario.resolve_tool_references extrai os tools do TEXTO da instruction
via regex `[Title](tool://slug)`. PATCH com `tools: [...]` é ignorado.
"""
from __future__ import annotations

import os
import sys

import httpx
from dotenv import load_dotenv

load_dotenv("../../follow_up_engine/.env")

SPX_BASE_URL = os.getenv("SPX_BASE_URL", "https://paulo.chatspx.app")
SPX_ACCOUNT_ID = int(os.getenv("SPX_ACCOUNT_ID", "1"))
SPX_USER_TOKEN = os.getenv("SPX_USER_TOKEN", "sxLWdXeSwLpNMBcG5FKMdRA6")
ASSISTANT_ID = 1

# Snippet markdown adicionado ao final do instruction.
TOOLS_BLOCK = """

## Ferramentas disponíveis

Você tem acesso às seguintes ferramentas. Use-as quando o caso pedir:

- [Buscar imóveis no Vista](tool://custom_buscar_imoveis_no_vista) — busca imóveis no CRM da Tozi com filtros (status_tipo, categoria, bairro, valor_max, dormitorios, ou bbox geográfico via latitude_min/max e longitude_min/max). Use quando o cliente pedir opções concretas ou tiver critérios específicos. Para buscar por proximidade, chame primeiro `buscar_localizacao` pra pegar o bbox.

- [Buscar localização (geocoding)](tool://custom_buscar_localizacao_geocoding) — converte uma referência geográfica em Sinop/MT (ex: "Unifasipe", "Hospital Regional") em latitude/longitude + bbox de proximidade ~3km. Use antes de `buscar_imoveis_no_vista` quando o cliente mencionar referência geográfica em vez de bairro.

Use as tools de forma natural na conversa — não anuncie "vou buscar" antes. Faça a busca, depois apresente o resultado ao cliente em texto humano (lista picada, máx 3 imóveis por mensagem)."""

# Quais scenarios recebem o bloco
TARGETS = ("Vendas", "Locação")


def main():
    hdr = {"api_access_token": SPX_USER_TOKEN, "Content-Type": "application/json"}
    list_url = f"{SPX_BASE_URL}/api/v1/accounts/{SPX_ACCOUNT_ID}/captain/assistants/{ASSISTANT_ID}/scenarios"
    r = httpx.get(list_url, headers=hdr, timeout=30.0)
    r.raise_for_status()
    scenarios = r.json().get("payload", [])

    for scen in scenarios:
        if scen["title"] not in TARGETS:
            print(f"skip '{scen['title']}' (not in {TARGETS})")
            continue
        instruction = scen.get("instruction") or ""
        if "tool://custom_buscar_imoveis_no_vista" in instruction:
            print(f"skip '{scen['title']}' (already has tool refs)")
            continue
        new_instruction = instruction.rstrip() + TOOLS_BLOCK

        url = f"{SPX_BASE_URL}/api/v1/accounts/{SPX_ACCOUNT_ID}/captain/assistants/{ASSISTANT_ID}/scenarios/{scen['id']}"
        body = {"instruction": new_instruction}
        rr = httpx.patch(url, headers=hdr, json=body, timeout=30.0)
        if rr.status_code >= 400:
            print(f"ERR '{scen['title']}': {rr.status_code} {rr.text}", file=sys.stderr)
            continue
        updated = rr.json()
        print(f"OK '{scen['title']}' (id={scen['id']}) → tools={updated.get('tools')}")


if __name__ == "__main__":
    main()
