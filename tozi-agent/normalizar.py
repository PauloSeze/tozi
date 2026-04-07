"""
Normalização de webhooks do SPX (ChatWoot).

Transforma o body cru do webhook em um Evento estruturado
e determina a rota de processamento.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class Evento:
    """Representação normalizada de um webhook do SPX."""

    conversa_id: int = 0
    sender_id: int = 0
    sender_type: str = "unknown"         # contact | user | agent_bot | unknown
    message_type: str = ""               # incoming | outgoing | activity
    content: str = ""
    private: bool = False
    em_atendimento: bool = False
    is_status_changed: bool = False
    status: str = ""                     # open | resolved | pending
    content_attrs: dict = field(default_factory=dict)
    source_id: str | None = None         # wamid da mensagem
    contact_source_id: str | None = None  # source_id do contact_inbox
    attachments: list[dict] = field(default_factory=list)
    nome_cliente: str = ""
    nome_atendente: str | None = None
    resumo_previo: str = ""
    custom_attributes: dict = field(default_factory=dict)
    inbox_id: int = 0

    @property
    def tem_anexo(self) -> bool:
        return len(self.attachments) > 0


def _detectar_sender_type(sender: dict, message_type: str) -> str:
    tipo = (sender.get("type") or "").lower()
    if tipo == "agent_bot":
        return "agent_bot"
    if tipo == "user":
        return "user"
    if tipo == "contact":
        return "contact"
    # Fallback: contato não tem campo "type"
    if sender.get("phone_number") or sender.get("identifier"):
        return "contact"
    if message_type == "incoming":
        return "contact"
    return "unknown"


def _detectar_em_atendimento(sender: dict, conversa: dict) -> bool:
    # 1. Labels da conversa (mais confiável)
    if "atendimento" in conversa.get("labels", []):
        return True
    # 2. Custom attributes da conversa
    if conversa.get("custom_attributes", {}).get("atendimento") is True:
        return True
    # 3. Custom attributes do contato/sender
    if sender.get("custom_attributes", {}).get("atendimento") is True:
        return True
    return False


def normalizar(body: dict) -> Evento:
    """Transforma o body cru do webhook SPX em um Evento."""

    event = body.get("event", "")
    evento = Evento()

    # --- Formato B: conversation_status_changed ---
    if event == "conversation_status_changed":
        evento.is_status_changed = True
        evento.conversa_id = body.get("id", 0)
        evento.status = body.get("status", "")
        evento.inbox_id = body.get("inbox_id", 0)
        return evento

    # --- Formato A: message_created ---
    sender = body.get("sender", {})
    conversa = body.get("conversation", {})
    meta = conversa.get("meta", {})

    evento.message_type = body.get("message_type", "")
    evento.content = body.get("content", "") or ""
    evento.private = body.get("private", False)
    evento.source_id = body.get("source_id")
    evento.attachments = body.get("attachments", [])
    evento.sender_id = sender.get("id", 0)
    evento.sender_type = _detectar_sender_type(sender, evento.message_type)

    # Content attributes (para detectar NPS)
    evento.content_attrs = body.get("content_attributes", {}) or {}

    # Conversa
    evento.conversa_id = conversa.get("id", 0)
    evento.inbox_id = conversa.get("inbox_id", 0)
    evento.custom_attributes = conversa.get("custom_attributes", {}) or {}
    evento.resumo_previo = evento.custom_attributes.get("resumo", "")

    # Contact inbox source_id (para detectar grupos @g.us)
    contact_inbox = conversa.get("contact_inbox", {}) or {}
    evento.contact_source_id = contact_inbox.get("source_id")

    # Nomes
    meta_sender = meta.get("sender", {}) or {}
    meta_assignee = meta.get("assignee", {}) or {}
    evento.nome_cliente = meta_sender.get("name", sender.get("name", ""))
    evento.nome_atendente = meta_assignee.get("name") if meta_assignee else None

    # Em atendimento
    evento.em_atendimento = _detectar_em_atendimento(sender, conversa)

    return evento


def determinar_rota(evento: Evento) -> str:
    """Determina a rota de processamento com base no evento normalizado."""

    # Bloqueios imediatos (ordem importa)
    if evento.is_status_changed:
        return "limpar_atendimento" if evento.status == "resolved" else "ignorar"

    if evento.message_type == "activity":
        return "ignorar"

    if evento.content_attrs.get("nps_survey"):
        return "ignorar"

    if evento.sender_type == "agent_bot":
        return "ignorar"

    if "@g.us" in (evento.source_id or "") or "@g.us" in (evento.contact_source_id or ""):
        return "ignorar"

    # Cliente
    if evento.sender_type == "contact":
        if evento.em_atendimento:
            return "ignorar"
        if not evento.content and not evento.tem_anexo:
            return "ignorar"
        return "agente_clara"

    # Atendente
    if evento.sender_type == "user":
        if evento.private:
            return "copiloto" if "#tozi" in evento.content.lower() else "ignorar"
        return "marcar_atendimento"

    return "ignorar"
