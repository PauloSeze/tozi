"""
Polling local — monitora a conversa no ChatWoot e dispara webhook local.
Substitui ngrok para testes de desenvolvimento.

Uso: python poll.py
"""

import sys
import io
import time
import httpx
from dotenv import load_dotenv

load_dotenv()

from config import SPX_BASE_URL, SPX_ACCOUNT_ID, SPX_BOT_TOKEN

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

CONVERSA_ID = 142
LOCAL_WEBHOOK = "http://localhost:8001/webhook/spx"
POLL_INTERVAL = 3  # segundos

headers = {"api_access_token": SPX_BOT_TOKEN}
ultimo_id = 0


def buscar_mensagens():
    url = f"{SPX_BASE_URL}/api/v1/accounts/{SPX_ACCOUNT_ID}/conversations/{CONVERSA_ID}/messages"
    r = httpx.get(url, headers=headers, timeout=10)
    r.raise_for_status()
    return r.json().get("payload", [])


def montar_webhook_body(msg, conversa):
    """Monta um body de webhook compatível com message_created."""
    return {
        "event": "message_created",
        "message_type": msg.get("message_type_str", "incoming") if "message_type_str" in msg else (
            "incoming" if msg.get("message_type") == 0 else "outgoing"
        ),
        "private": msg.get("private", False),
        "content": msg.get("content", "") or "",
        "attachments": msg.get("attachments", []),
        "source_id": msg.get("source_id"),
        "id": msg.get("id"),
        "content_attributes": msg.get("content_attributes", {}),
        "sender": msg.get("sender", {}),
        "conversation": conversa,
    }


def buscar_conversa():
    url = f"{SPX_BASE_URL}/api/v1/accounts/{SPX_ACCOUNT_ID}/conversations/{CONVERSA_ID}"
    r = httpx.get(url, headers=headers, timeout=10)
    r.raise_for_status()
    return r.json()


def disparar_local(body):
    r = httpx.post(LOCAL_WEBHOOK, json=body, timeout=30)
    return r.json()


def main():
    global ultimo_id
    print(f"Monitorando conversa {CONVERSA_ID} — poll a cada {POLL_INTERVAL}s")
    print(f"Webhook local: {LOCAL_WEBHOOK}")
    print("Mande uma mensagem no WhatsApp...\n")

    # Pegar último ID para não processar mensagens antigas
    msgs = buscar_mensagens()
    if msgs:
        ultimo_id = max(m["id"] for m in msgs)
        print(f"Último ID existente: {ultimo_id} — aguardando novas mensagens\n")

    conversa = buscar_conversa()

    while True:
        try:
            msgs = buscar_mensagens()
            novas = [m for m in msgs if m["id"] > ultimo_id]

            for msg in sorted(novas, key=lambda m: m["id"]):
                tipo = "incoming" if msg.get("message_type") == 0 else "outgoing"
                sender_name = msg.get("sender", {}).get("name", "?")
                content = (msg.get("content") or "")[:80]
                print(f"[{tipo}] {sender_name}: {content}")

                # Só processar incoming (mensagens do cliente)
                if msg.get("message_type") == 0:
                    body = montar_webhook_body(msg, conversa)
                    resultado = disparar_local(body)
                    print(f"  -> webhook: {resultado}\n")
                else:
                    print(f"  -> ignorado (outgoing)\n")

                ultimo_id = msg["id"]

        except KeyboardInterrupt:
            print("\nParando...")
            break
        except Exception as e:
            print(f"Erro: {e}")

        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    main()
