"""Cliente SPX (ChatWoot fork) — criar contato, criar conversa, enviar mensagem proativa."""
from __future__ import annotations

import logging
import re
from dataclasses import dataclass

import httpx

log = logging.getLogger(__name__)


@dataclass
class Contact:
    id: int
    name: str | None
    phone_number: str | None
    identifier: str | None


@dataclass
class Conversation:
    id: int
    contact_id: int
    inbox_id: int
    status: str
    custom_attributes: dict


class SpxClient:
    def __init__(self, base_url: str, account_id: int, user_token: str,
                 inbox_id: int, inbox_identifier: str, timeout: float = 30.0):
        self.base_url = base_url.rstrip("/")
        self.account_id = account_id
        self.inbox_id = inbox_id
        self.inbox_identifier = inbox_identifier
        self.user_token = user_token
        self._client = httpx.Client(
            timeout=timeout,
            headers={"api_access_token": user_token, "Content-Type": "application/json"},
        )

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self._client.close()

    @staticmethod
    def normalize_phone_br(phone: str) -> str:
        """Normaliza pra E.164 brasileiro com 55 + DDD + 9 dígitos do celular."""
        digits = re.sub(r"\D", "", phone)
        if digits.startswith("55") and len(digits) in (12, 13):
            local = digits[4:]
            ddd = digits[2:4]
            if len(local) == 8:  # falta o 9
                local = "9" + local
            return f"+55{ddd}{local}"
        if len(digits) in (10, 11):
            local = digits[2:]
            ddd = digits[:2]
            if len(local) == 8:
                local = "9" + local
            return f"+55{ddd}{local}"
        return f"+{digits}"

    def search_contact_by_phone(self, phone_e164: str) -> Contact | None:
        url = f"{self.base_url}/api/v1/accounts/{self.account_id}/contacts/search"
        r = self._client.get(url, params={"q": phone_e164, "include": "phone_number"})
        r.raise_for_status()
        payload = r.json().get("payload", [])
        for item in payload:
            if item.get("phone_number") == phone_e164:
                return Contact(
                    id=item["id"],
                    name=item.get("name"),
                    phone_number=item.get("phone_number"),
                    identifier=item.get("identifier"),
                )
        return None

    def has_open_conversation(self, contact_id: int) -> bool:
        url = f"{self.base_url}/api/v1/accounts/{self.account_id}/contacts/{contact_id}/conversations"
        r = self._client.get(url)
        r.raise_for_status()
        for conv in r.json().get("payload", []):
            if conv.get("status") in ("open", "pending"):
                return True
        return False

    def create_contact(self, name: str, phone_e164: str) -> Contact:
        url = f"{self.base_url}/api/v1/accounts/{self.account_id}/contacts"
        body = {
            "name": name,
            "phone_number": phone_e164,
            "inbox_id": self.inbox_id,
        }
        r = self._client.post(url, json=body)
        r.raise_for_status()
        data = r.json().get("payload", r.json()).get("contact", r.json())
        # SPX retorna `{payload: {contact: {...}}}` ou similar — defensivo
        cdata = data if isinstance(data, dict) and "id" in data else data.get("contact", data)
        return Contact(
            id=cdata["id"],
            name=cdata.get("name"),
            phone_number=cdata.get("phone_number"),
            identifier=cdata.get("identifier"),
        )

    def create_conversation(self, contact_id: int, source_id: str,
                             first_message: str, custom_attributes: dict | None = None) -> Conversation:
        url = f"{self.base_url}/api/v1/accounts/{self.account_id}/conversations"
        body = {
            "source_id": source_id,
            "inbox_id": self.inbox_id,
            "contact_id": contact_id,
            "status": "open",
            "message": {"content": first_message},
        }
        if custom_attributes:
            body["custom_attributes"] = custom_attributes
        r = self._client.post(url, json=body)
        r.raise_for_status()
        data = r.json()
        return Conversation(
            id=data["id"],
            contact_id=data.get("contact_id", contact_id),
            inbox_id=data.get("inbox_id", self.inbox_id),
            status=data.get("status", "open"),
            custom_attributes=data.get("custom_attributes", {}),
        )

    def send_message(self, conversation_id: int, content: str, private: bool = False) -> dict:
        url = f"{self.base_url}/api/v1/accounts/{self.account_id}/conversations/{conversation_id}/messages"
        body = {"content": content, "message_type": "outgoing", "private": private}
        r = self._client.post(url, json=body)
        r.raise_for_status()
        return r.json()

    def update_conversation_custom_attributes(self, conversation_id: int, attrs: dict) -> dict:
        url = f"{self.base_url}/api/v1/accounts/{self.account_id}/conversations/{conversation_id}/custom_attributes"
        r = self._client.post(url, json={"custom_attributes": attrs})
        r.raise_for_status()
        return r.json()
