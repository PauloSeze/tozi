"""Testes da normalização e roteamento de webhooks SPX."""

import copy
import json
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from normalizar import Evento, determinar_rota, normalizar

WEBHOOKS_DIR = Path(__file__).parent / "webhooks"


def _carregar(nome: str) -> dict:
    return json.loads((WEBHOOKS_DIR / nome).read_text(encoding="utf-8"))


# --- w1: texto incoming com label atendimento → ignorar (em_atendimento) ---

def test_w1_texto_com_label_atendimento_ignorado():
    """Label 'atendimento' presente → em_atendimento = True → ignorar."""
    body = _carregar("w1_texto_incoming.json")
    evento = normalizar(body)

    assert evento.conversa_id == 2159
    assert evento.sender_type == "contact"
    assert evento.em_atendimento is True
    assert determinar_rota(evento) == "ignorar"


def test_w1_sem_label_atendimento_vai_para_clara():
    """Sem label 'atendimento' e sem custom_attributes → agente_clara."""
    body = _carregar("w1_texto_incoming.json")
    body["conversation"]["labels"] = []
    body["conversation"]["custom_attributes"] = {}

    evento = normalizar(body)

    assert evento.sender_type == "contact"
    assert evento.em_atendimento is False
    assert determinar_rota(evento) == "agente_clara"


# --- w2: imagem incoming sem atendimento → agente_clara ---

def test_w2_imagem_sem_atendimento_vai_para_clara():
    """Imagem de contato sem flag de atendimento → agente_clara."""
    body = _carregar("w2_imagem_incoming.json")
    evento = normalizar(body)

    assert evento.sender_type == "contact"
    assert evento.tem_anexo is True
    assert evento.attachments[0]["file_type"] == "image"
    assert evento.em_atendimento is False
    assert determinar_rota(evento) == "agente_clara"


# --- w3: outgoing público de atendente → marcar_atendimento ---

def test_w3_outgoing_publico_marca_atendimento():
    """Mensagem pública de atendente (user) → marcar_atendimento."""
    body = _carregar("w3_outgoing_publico.json")
    evento = normalizar(body)

    assert evento.sender_type == "user"
    assert evento.private is False
    assert determinar_rota(evento) == "marcar_atendimento"


# --- w4: outgoing privado com #tozi → copiloto ---

def test_w4_tozi_privado_vai_para_copiloto():
    """Mensagem privada com #tozi de atendente → copiloto."""
    body = _carregar("w4_outgoing_privado_tozi.json")
    evento = normalizar(body)

    assert evento.sender_type == "user"
    assert evento.private is True
    assert "#tozi" in evento.content.lower()
    assert determinar_rota(evento) == "copiloto"


def test_w4_privado_sem_tozi_ignorado():
    """Mensagem privada SEM #tozi → ignorar."""
    body = _carregar("w4_outgoing_privado_tozi.json")
    body["content"] = "anotação interna qualquer"

    evento = normalizar(body)

    assert evento.sender_type == "user"
    assert evento.private is True
    assert determinar_rota(evento) == "ignorar"


# --- w5: status resolved → limpar_atendimento ---

def test_w5_resolved_limpa_atendimento():
    """conversation_status_changed com resolved → limpar_atendimento."""
    body = _carregar("w5_status_resolved.json")
    evento = normalizar(body)

    assert evento.is_status_changed is True
    assert evento.conversa_id == 2159  # vem de body.id, não body.conversation.id
    assert evento.status == "resolved"
    assert determinar_rota(evento) == "limpar_atendimento"


def test_status_changed_nao_resolved_ignorado():
    """conversation_status_changed com status != resolved → ignorar."""
    body = _carregar("w5_status_resolved.json")
    body["status"] = "open"

    evento = normalizar(body)

    assert evento.is_status_changed is True
    assert determinar_rota(evento) == "ignorar"


# --- Grupo WhatsApp (@g.us) → ignorar ---

def test_grupo_ignorado():
    """Mensagem de grupo (@g.us no contact_inbox) → ignorar."""
    body = _carregar("w1_texto_incoming.json")
    body["conversation"]["labels"] = []
    body["conversation"]["custom_attributes"] = {}
    body["conversation"]["contact_inbox"]["source_id"] = "556696350491-1234@g.us"

    evento = normalizar(body)
    assert determinar_rota(evento) == "ignorar"


# --- Agent bot → ignorar ---

def test_agent_bot_ignorado():
    """Mensagem de agent_bot → ignorar."""
    body = _carregar("w1_texto_incoming.json")
    body["sender"]["type"] = "agent_bot"
    body["conversation"]["labels"] = []

    evento = normalizar(body)

    assert evento.sender_type == "agent_bot"
    assert determinar_rota(evento) == "ignorar"


# --- Sender sem type detectado como contact ---

def test_sender_sem_type_detectado_como_contact():
    """Sender sem campo 'type' mas com phone_number → contact → agente_clara."""
    body = _carregar("w1_texto_incoming.json")
    body["conversation"]["labels"] = []
    body["conversation"]["custom_attributes"] = {}
    # Sender sem "type" (cenário real de contato WhatsApp)
    assert "type" not in body["sender"]

    evento = normalizar(body)

    assert evento.sender_type == "contact"
    assert determinar_rota(evento) == "agente_clara"


# --- Em atendimento via custom_attributes do sender ---

def test_em_atendimento_via_sender_custom_attributes():
    """atendimento=True no sender.custom_attributes → em_atendimento."""
    body = _carregar("w1_texto_incoming.json")
    body["conversation"]["labels"] = []
    body["conversation"]["custom_attributes"] = {}
    body["sender"]["custom_attributes"] = {"atendimento": True}

    evento = normalizar(body)

    assert evento.em_atendimento is True
    assert determinar_rota(evento) == "ignorar"


# --- Em atendimento via custom_attributes da conversa ---

def test_em_atendimento_via_conversa_custom_attributes():
    """atendimento=True no conversation.custom_attributes → em_atendimento."""
    body = _carregar("w1_texto_incoming.json")
    body["conversation"]["labels"] = []
    body["conversation"]["custom_attributes"] = {"atendimento": True}
    body["sender"]["custom_attributes"] = {}

    evento = normalizar(body)

    assert evento.em_atendimento is True
    assert determinar_rota(evento) == "ignorar"


# --- NPS survey → ignorar ---

def test_nps_survey_ignorado():
    """Mensagem com content_attributes.nps_survey → ignorar."""
    body = _carregar("w1_texto_incoming.json")
    body["conversation"]["labels"] = []
    body["content_attributes"] = {"nps_survey": True}

    evento = normalizar(body)
    assert determinar_rota(evento) == "ignorar"


# --- Activity message → ignorar ---

def test_activity_message_ignorado():
    """message_type = activity → ignorar."""
    body = _carregar("w1_texto_incoming.json")
    body["message_type"] = "activity"
    body["conversation"]["labels"] = []

    evento = normalizar(body)
    assert determinar_rota(evento) == "ignorar"


# --- Contato sem conteúdo e sem anexo → ignorar ---

def test_contato_sem_conteudo_sem_anexo_ignorado():
    """Contato envia mensagem vazia sem anexo → ignorar."""
    body = _carregar("w1_texto_incoming.json")
    body["conversation"]["labels"] = []
    body["conversation"]["custom_attributes"] = {}
    body["content"] = ""
    body["attachments"] = []

    evento = normalizar(body)

    assert evento.sender_type == "contact"
    assert not evento.content
    assert not evento.tem_anexo
    assert determinar_rota(evento) == "ignorar"
