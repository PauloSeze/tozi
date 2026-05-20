"""Cria no SPX (chatwoot) o que falta pro follow-up ficar VISÍVEL no front.

Hoje o engine grava custom_attributes nas conversas (tozi_status_lead,
tozi_followup_attempts, etc.) mas NÃO existem as *definições* desses atributos
no account — então o chatwoot não renderiza nada no sidebar. Este script cria
as definições (idempotente) + labels pra um "folder" filtrável de follow-up.

Rode UMA vez (estando na rede da PAULAO ou apontando pra base do SPX):
    cd /home/paulo/tozi-followup && .venv/bin/python setup_spx_front.py

Usa as mesmas envs do engine: SPX_BASE_URL, SPX_ACCOUNT_ID, SPX_USER_TOKEN.
"""
from __future__ import annotations

import os
import sys

import httpx
from dotenv import load_dotenv

load_dotenv()

BASE = os.environ["SPX_BASE_URL"].rstrip("/")
ACCOUNT = int(os.environ["SPX_ACCOUNT_ID"])
TOKEN = os.environ["SPX_USER_TOKEN"]

HEADERS = {"api_access_token": TOKEN, "Content-Type": "application/json"}

# attribute_key precisa casar EXATAMENTE com o que o engine grava (engine.py).
# O chatwoot deriva attribute_key de attribute_display_name via parameterize('_'),
# então os display_names abaixo foram escolhidos pra gerar exatamente essas keys.
CONV_ATTRS = [
    {
        "attribute_display_name": "Tozi Status Lead",
        "attribute_key": "tozi_status_lead",
        "attribute_display_type": "list",
        "attribute_values": ["novo", "em_contato", "qualificado", "esfriado", "perdido", "convertido"],
        "attribute_description": "Estágio do lead no funil (setado pelo engine de follow-up).",
    },
    {
        "attribute_display_name": "Tozi Fonte",
        "attribute_key": "tozi_fonte",
        "attribute_display_type": "list",
        "attribute_values": ["META_ADS", "SITE", "INSTAGRAM", "FORMS_FINANCIAMENTO", "CHATBOT", "loft", "vista"],
        "attribute_description": "Origem do lead (campanha/canal de captação).",
    },
    {
        "attribute_display_name": "Tozi Followup Attempts",
        "attribute_key": "tozi_followup_attempts",
        "attribute_display_type": "number",
        "attribute_description": "Quantas reabordagens automáticas já foram enviadas.",
    },
    {
        "attribute_display_name": "Tozi Last Followup Day",
        "attribute_key": "tozi_last_followup_day",
        "attribute_display_type": "number",
        "attribute_description": "D+N da última reabordagem disparada.",
    },
    {
        "attribute_display_name": "Tozi Vista Codigo",
        "attribute_key": "tozi_vista_codigo",
        "attribute_display_type": "text",
        "attribute_description": "Código do lead/cliente no Vista CRM.",
    },
]

LABELS = [
    {"title": "lead-novo", "description": "Lead novo captado pela prospecção ativa", "color": "#1f93ff"},
    {"title": "followup-ativo", "description": "Conversa em cadência de follow-up automático", "color": "#ff9800"},
    {"title": "lead-esfriado", "description": "Lead sem resposta após várias reabordagens", "color": "#9e9e9e"},
]


def existing_attr_keys(client: httpx.Client) -> set[str]:
    r = client.get(
        f"{BASE}/api/v1/accounts/{ACCOUNT}/custom_attribute_definitions",
        params={"attribute_model": "conversation_attribute"},
    )
    r.raise_for_status()
    return {d.get("attribute_key") for d in r.json()}


def existing_labels(client: httpx.Client) -> set[str]:
    r = client.get(f"{BASE}/api/v1/accounts/{ACCOUNT}/labels")
    r.raise_for_status()
    payload = r.json().get("payload", r.json()) if isinstance(r.json(), dict) else r.json()
    return {l.get("title") for l in payload}


def main() -> int:
    with httpx.Client(headers=HEADERS, timeout=30.0) as client:
        have = existing_attr_keys(client)
        for attr in CONV_ATTRS:
            if attr["attribute_key"] in have:
                print(f"  attr ok (existe): {attr['attribute_key']}")
                continue
            body = {"attribute_model": "conversation_attribute", **attr}
            r = client.post(f"{BASE}/api/v1/accounts/{ACCOUNT}/custom_attribute_definitions", json=body)
            if r.status_code in (200, 201):
                created = r.json().get("attribute_key")
                flag = "OK" if created == attr["attribute_key"] else f"ATENCAO key gerada={created}"
                print(f"  attr criado: {attr['attribute_key']} -> {flag}")
            else:
                print(f"  ERRO attr {attr['attribute_key']}: HTTP {r.status_code} {r.text[:200]}")

        have_labels = existing_labels(client)
        for label in LABELS:
            if label["title"] in have_labels:
                print(f"  label ok (existe): {label['title']}")
                continue
            r = client.post(f"{BASE}/api/v1/accounts/{ACCOUNT}/labels", json=label)
            print(f"  label {label['title']}: HTTP {r.status_code}")
    print("done")
    return 0


if __name__ == "__main__":
    sys.exit(main())
