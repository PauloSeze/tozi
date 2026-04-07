#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para setar custom attribute "atendimento": true em todas as conversas abertas do Chatwoot.

Uso:
    python chatwoot_set_atendimento.py --api-key YOUR_API_KEY

    Ou via variável de ambiente:
    export CHATWOOT_API_KEY=YOUR_API_KEY
    python chatwoot_set_atendimento.py
"""

import argparse
import os
import sys
import time
import requests
from typing import Optional

# Fix encoding no Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')


# Configurações
BASE_URL = "https://chat.simplexsolucoes.com.br"
ACCOUNT_ID = 6
DELAY_BETWEEN_REQUESTS = 0.5  # segundos


def get_conversations(api_key: str, page: int = 1) -> dict:
    """Busca uma página de conversas abertas."""
    url = f"{BASE_URL}/api/v1/accounts/{ACCOUNT_ID}/conversations"
    params = {"status": "open", "page": page}

    headers = {"api_access_token": api_key}

    response = requests.get(url, params=params, headers=headers, timeout=30)
    response.raise_for_status()
    return response.json()


def get_all_conversations(api_key: str) -> list:
    """Busca todas as conversas abertas com paginação por page."""
    all_conversations = []
    page = 1

    print("Buscando conversas abertas...")

    # Primeiro, pegar o total esperado
    first_data = get_conversations(api_key, 1)
    total_expected = first_data.get("data", {}).get("meta", {}).get("all_count", 0)
    print(f"  Total esperado: {total_expected} conversas")

    while True:
        try:
            print(f"  Pagina {page}...", end=" ", flush=True)
            data = get_conversations(api_key, page)

            conversations = data.get("data", {}).get("payload", [])

            if not conversations:
                print("vazia (fim)")
                break

            all_conversations.extend(conversations)
            print(f"{len(conversations)} conversas (total: {len(all_conversations)}/{total_expected})")

            # Se já pegou todas, para
            if len(all_conversations) >= total_expected:
                print("  Todas as conversas buscadas!")
                break

            page += 1
            time.sleep(DELAY_BETWEEN_REQUESTS)

        except requests.exceptions.HTTPError as e:
            print(f"erro HTTP {e.response.status_code}")
            if e.response.status_code == 500:
                # Tenta continuar na próxima página
                print(f"  Tentando página {page + 1}...")
                page += 1
                continue
            raise

    return all_conversations


def set_custom_attribute(api_key: str, conversation_id: int, attributes: dict) -> bool:
    """Seta custom attributes em uma conversa."""
    url = f"{BASE_URL}/api/v1/accounts/{ACCOUNT_ID}/conversations/{conversation_id}/custom_attributes"
    headers = {"api_access_token": api_key}
    payload = {"custom_attributes": attributes}

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        print(f"    Erro: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Seta atendimento=true em conversas abertas do Chatwoot")
    parser.add_argument("--api-key", help="API key do Chatwoot")
    parser.add_argument("--dry-run", action="store_true", help="Apenas lista, não modifica")
    parser.add_argument("--limit", type=int, help="Limitar número de conversas processadas")
    args = parser.parse_args()

    # Obter API key
    api_key = args.api_key or os.environ.get("CHATWOOT_API_KEY")
    if not api_key:
        print("Erro: API key não fornecida. Use --api-key ou defina CHATWOOT_API_KEY")
        sys.exit(1)

    # Buscar todas as conversas
    try:
        conversations = get_all_conversations(api_key)
    except requests.exceptions.RequestException as e:
        print(f"Erro ao buscar conversas: {e}")
        sys.exit(1)

    print(f"\nTotal de conversas abertas: {len(conversations)}")

    if args.limit:
        conversations = conversations[:args.limit]
        print(f"Limitado a {args.limit} conversas")

    if args.dry_run:
        print("\n[DRY RUN] Conversas que seriam atualizadas:")
        for conv in conversations[:10]:
            print(f"  - ID {conv['id']}: {conv.get('meta', {}).get('sender', {}).get('name', 'N/A')}")
        if len(conversations) > 10:
            print(f"  ... e mais {len(conversations) - 10} conversas")
        return

    # Setar atributos
    print(f"\nSetando atendimento=true em {len(conversations)} conversas...")

    success = 0
    failed = 0

    for i, conv in enumerate(conversations, 1):
        conv_id = conv["id"]
        sender_name = conv.get("meta", {}).get("sender", {}).get("name", "N/A")

        print(f"  [{i}/{len(conversations)}] Conversa {conv_id} ({sender_name})...", end=" ", flush=True)

        if set_custom_attribute(api_key, conv_id, {"atendimento": True}):
            print("OK")
            success += 1
        else:
            print("FALHOU")
            failed += 1

        time.sleep(DELAY_BETWEEN_REQUESTS)

    print(f"\nConcluído!")
    print(f"  Sucesso: {success}")
    print(f"  Falhas: {failed}")


if __name__ == "__main__":
    main()
