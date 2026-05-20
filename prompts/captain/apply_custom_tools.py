"""Aplica os Custom Tools Tozi via API do Captain.

Depois que o fix de SafeEndpointValidatable estiver deployado em paulo.chatspx.app,
roda esse script pra criar/atualizar os 2 Custom Tools e linká-los aos Scenarios.

Uso:
    cd tozi/prompts/captain
    python apply_custom_tools.py
    python apply_custom_tools.py --dry-run  # só lista o que faria
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import httpx
from dotenv import load_dotenv

HERE = Path(__file__).parent
PAYLOADS_DIR = HERE / "_payloads"

load_dotenv(HERE.parent.parent / "follow_up_engine" / ".env")  # reusa .env do follow_up_engine

SPX_BASE_URL = os.getenv("SPX_BASE_URL", "https://paulo.chatspx.app")
SPX_ACCOUNT_ID = int(os.getenv("SPX_ACCOUNT_ID", "1"))
SPX_USER_TOKEN = os.getenv("SPX_USER_TOKEN", "sxLWdXeSwLpNMBcG5FKMdRA6")
ASSISTANT_ID = int(os.getenv("CLARA_ASSISTANT_ID", "1"))


TOOLS_TO_APPLY = [
    "tool-buscar-imoveis-vista.json",
    "tool-buscar-localizacao.json",
]

# Quais scenarios usam quais tools
SCENARIO_TOOL_BINDINGS = {
    "Vendas":   ["custom_buscar_imoveis_no_vista", "custom_buscar_localizacao_geocoding"],
    "Locação":  ["custom_buscar_imoveis_no_vista", "custom_buscar_localizacao_geocoding"],
    # Suporte não usa essas tools — só faq_lookup nativo
}


def hdr() -> dict:
    return {"api_access_token": SPX_USER_TOKEN, "Content-Type": "application/json"}


def list_custom_tools() -> list[dict]:
    url = f"{SPX_BASE_URL}/api/v1/accounts/{SPX_ACCOUNT_ID}/captain/custom_tools"
    r = httpx.get(url, headers=hdr(), timeout=30.0)
    r.raise_for_status()
    return r.json().get("payload", [])


def apply_tool(payload_path: Path, dry_run: bool = False) -> dict:
    payload = json.loads(payload_path.read_text(encoding="utf-8"))
    existing = next((t for t in list_custom_tools() if t["title"] == payload["title"]), None)

    url_base = f"{SPX_BASE_URL}/api/v1/accounts/{SPX_ACCOUNT_ID}/captain/custom_tools"
    if existing:
        method = "PATCH"
        url = f"{url_base}/{existing['id']}"
        action = "update"
    else:
        method = "POST"
        url = url_base
        action = "create"

    if dry_run:
        print(f"[DRY] {action} {payload['title']} → {method} {url}")
        return {"action": action, "dry": True}

    r = httpx.request(method, url, headers=hdr(), json=payload, timeout=30.0)
    if r.status_code >= 400:
        print(f"ERR {action} {payload['title']}: {r.status_code} {r.text}", file=sys.stderr)
        r.raise_for_status()
    data = r.json()
    print(f"OK {action} tool id={data['id']} slug={data['slug']}")
    return data


def list_scenarios() -> list[dict]:
    url = f"{SPX_BASE_URL}/api/v1/accounts/{SPX_ACCOUNT_ID}/captain/assistants/{ASSISTANT_ID}/scenarios"
    r = httpx.get(url, headers=hdr(), timeout=30.0)
    r.raise_for_status()
    return r.json().get("payload", [])


def bind_tools_to_scenarios(dry_run: bool = False):
    """Atualiza cada Scenario com a lista de tools que ele pode usar."""
    scenarios = list_scenarios()
    available = {t["slug"]: t for t in list_custom_tools()}

    for scen in scenarios:
        title = scen["title"]
        wanted = SCENARIO_TOOL_BINDINGS.get(title)
        if not wanted:
            continue
        # filtra apenas as que existem
        existing_slugs = [s for s in wanted if s in available]
        missing = set(wanted) - set(existing_slugs)
        if missing:
            print(f"WARN scenario '{title}' wants {missing} but they don't exist as custom_tools yet", file=sys.stderr)

        url = f"{SPX_BASE_URL}/api/v1/accounts/{SPX_ACCOUNT_ID}/captain/assistants/{ASSISTANT_ID}/scenarios/{scen['id']}"
        body = {"tools": existing_slugs}
        if dry_run:
            print(f"[DRY] bind scenario '{title}' (id={scen['id']}) → tools={existing_slugs}")
            continue
        r = httpx.patch(url, headers=hdr(), json=body, timeout=30.0)
        if r.status_code >= 400:
            print(f"ERR bind scenario '{title}': {r.status_code} {r.text}", file=sys.stderr)
            continue
        print(f"OK bound scenario '{title}' (id={scen['id']}) → tools={existing_slugs}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    print(f"=== Applying Tozi Custom Tools to {SPX_BASE_URL} account {SPX_ACCOUNT_ID} ===")
    for filename in TOOLS_TO_APPLY:
        apply_tool(PAYLOADS_DIR / filename, dry_run=args.dry_run)

    print("\n=== Binding tools to scenarios ===")
    bind_tools_to_scenarios(dry_run=args.dry_run)

    print("\nPronto. Próximo passo: smoke test mandando mensagem no SPX.")


if __name__ == "__main__":
    main()
