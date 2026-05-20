"""Lógica de SDR Passivo (polling Vista + disparo) e Follow-up."""
from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone

from .config import Config
from .spx import SpxClient
from .templates import render_followup, render_initial
from .vista import Lead, VistaClient

log = logging.getLogger(__name__)


class Engine:
    def __init__(self, cfg: Config):
        self.cfg = cfg

    def _new_vista(self) -> VistaClient:
        return VistaClient(self.cfg.vista_base_url, self.cfg.vista_api_key)

    def _new_spx(self) -> SpxClient:
        return SpxClient(
            base_url=self.cfg.spx_base_url,
            account_id=self.cfg.spx_account_id,
            user_token=self.cfg.spx_user_token,
            inbox_id=self.cfg.spx_inbox_id,
            inbox_identifier=self.cfg.spx_inbox_identifier,
        )

    # ── SDR Passivo ─────────────────────────────────────────────────────────
    def poll_new_leads(self, *, dry_run: bool = False) -> dict:
        """Detecta leads novos no bucket Vista e dispara primeira mensagem via SPX."""
        cutoff = (datetime.now(timezone.utc) - timedelta(hours=24)).strftime("%Y-%m-%d")
        stats = {"vista_found": 0, "already_have_conv": 0, "sent": 0, "errors": 0}

        with self._new_vista() as vista, self._new_spx() as spx:
            leads = vista.listar_clientes(
                bucket_corretor_id=self.cfg.vista_bucket_lead_user_id,
                data_desde=cutoff,
            )
            stats["vista_found"] = len(leads)

            for lead in leads:
                try:
                    # enrich pra pegar Celular (não vem em /clientes/listar)
                    vista.enrich_lead_with_celular(lead)
                    if not lead.telefones:
                        log.debug("skip lead %s sem telefone", lead.codigo)
                        continue
                    phone_e164 = spx.normalize_phone_br(lead.telefones[0])

                    contact = spx.search_contact_by_phone(phone_e164)
                    if contact and spx.has_open_conversation(contact.id):
                        stats["already_have_conv"] += 1
                        continue

                    if not contact:
                        if dry_run:
                            log.info("[DRY] criaria contact %s (%s)", lead.nome, phone_e164)
                        else:
                            contact = spx.create_contact(lead.nome or "Lead Tozi", phone_e164)

                    message = render_initial(lead.veiculo_captacao, lead.nome or "")

                    if dry_run:
                        log.info("[DRY] disparo %s → %s: %s", phone_e164, contact.id if contact else "?", message[:60])
                    else:
                        conv = spx.create_conversation(
                            contact_id=contact.id,
                            source_id=phone_e164.lstrip("+"),
                            first_message=message,
                            custom_attributes={
                                "tozi_vista_codigo": lead.codigo,
                                "tozi_fonte": lead.veiculo_captacao or "",
                                "tozi_followup_attempts": 0,
                                "tozi_status_lead": "novo",
                            },
                        )
                        spx.add_labels(conv.id, ["lead-novo"])
                    stats["sent"] += 1
                except Exception as e:
                    stats["errors"] += 1
                    log.exception("erro processando lead %s: %s", lead.codigo, e)

        return stats

    # ── Follow-up ───────────────────────────────────────────────────────────
    def run_followup(self, *, dry_run: bool = False) -> dict:
        """Reabordagem D+N para conversas sem resposta do cliente."""
        stats = {"checked": 0, "sent": 0, "skipped_max_attempts": 0, "errors": 0}
        with self._new_spx() as spx:
            # listagem básica: conversas open com label específica seria ideal, mas pra MVP usamos custom_attributes
            url = f"{spx.base_url}/api/v1/accounts/{spx.account_id}/conversations"
            r = spx._client.get(url, params={"status": "open", "page": 1})
            r.raise_for_status()
            convs = r.json().get("data", {}).get("payload", [])

            for conv in convs:
                stats["checked"] += 1
                try:
                    attrs = conv.get("custom_attributes") or {}
                    attempts = int(attrs.get("tozi_followup_attempts") or 0)
                    if attempts >= self.cfg.followup_max_attempts:
                        stats["skipped_max_attempts"] += 1
                        continue

                    # tempo desde a última mensagem do CLIENTE
                    last_activity = conv.get("last_activity_at") or conv.get("last_non_activity_message", {}).get("created_at")
                    if not last_activity:
                        continue
                    last_dt = datetime.fromtimestamp(int(last_activity), tz=timezone.utc)
                    days_since = (datetime.now(timezone.utc) - last_dt).days
                    if days_since not in self.cfg.followup_days:
                        continue

                    nome = (conv.get("meta") or {}).get("sender", {}).get("name") or ""
                    message = render_followup(days_since, nome)
                    if not message:
                        continue

                    if dry_run:
                        log.info("[DRY] followup conv %s D+%d: %s", conv["id"], days_since, message[:60])
                    else:
                        spx.send_message(conv["id"], message)
                        new_attempts = attempts + 1
                        spx.update_conversation_custom_attributes(conv["id"], {
                            "tozi_followup_attempts": new_attempts,
                            "tozi_last_followup_day": days_since,
                        })
                        labels = ["followup-ativo"]
                        if new_attempts >= self.cfg.followup_max_attempts:
                            labels.append("lead-esfriado")
                        spx.add_labels(conv["id"], labels)
                    stats["sent"] += 1
                except Exception as e:
                    stats["errors"] += 1
                    log.exception("erro followup conv %s: %s", conv.get("id"), e)
        return stats

    # ── BDR ─────────────────────────────────────────────────────────────────
    def run_bdr(self, *, dry_run: bool = False) -> dict:
        """Varredura mensal: leads na base Vista com DataUltimaInteracao > 90 dias e Etapa preenchida.

        Estratégia: separado do polling pq usa critério diferente — leads QUALIFICADOS que esfriaram,
        não leads novos. Mensagem de reativação tem tom diferente.
        """
        # Stub — exige campo DataUltimaInteracao do Vista que pode não estar disponível em todos os endpoints.
        # Marcar como TODO até confirmar capacidade Vista API.
        stats = {"vista_found": 0, "sent": 0, "errors": 0}
        log.warning("BDR ainda não implementado — depende de Vista DataUltimaInteracao + decisão de mensagem")
        return stats
