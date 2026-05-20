"""Cliente Vista CRM (Loft) — leitura de leads, clientes, negócios.

Particularidades da Vista API descobertas em produção:
- Exige header `Accept: application/json` (sem ele, 406).
- `/clientes/listar` aceita um SUBSET de campos. Telefones NÃO está no listar.
- `/clientes/detalhes?cliente=ID` retorna campos adicionais — incluindo `Celular`.
- Resposta de listar pode vir como `{ "codigo1": {...}, "codigo2": {...} }` (dict) em vez de list.
- Filtros server-side: `filter.Corretor` (string), `filter.DataCadastro` (array [from, to]).
  Combinar Corretor + DataCadastro às vezes retorna "sem resultados" mesmo havendo —
  preferimos filtrar Corretor server-side e DataCadastro client-side.
"""
from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass, field
from typing import Any

import httpx

log = logging.getLogger(__name__)


@dataclass
class Lead:
    codigo: str
    nome: str
    telefones: list[str] = field(default_factory=list)
    email: str | None = None
    veiculo_captacao: str | None = None
    data_cadastro: str | None = None
    etapa: str | None = None
    corretor_id: int | None = None
    raw: dict[str, Any] = field(default_factory=dict)


class VistaClient:
    LISTAR_FIELDS_DEFAULT = (
        "Codigo", "Nome", "VeiculoCaptacao", "DataCadastro", "Corretor",
    )
    DETALHES_FIELDS_DEFAULT = (
        "Codigo", "Nome", "Celular", "VeiculoCaptacao", "DataCadastro", "Corretor",
    )

    def __init__(self, base_url: str, api_key: str, timeout: float = 30.0):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        # Vista API exige Accept: application/json — sem isso retorna 406
        self._client = httpx.Client(timeout=timeout, headers={"Accept": "application/json"})

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self._client.close()

    def _build_search(self, fields: list[str], filter_: dict | None = None, order: dict | None = None,
                       pagina: int = 1, quantidade: int = 50) -> str:
        return json.dumps({
            "fields": fields,
            "filter": filter_ or {},
            "advFilter": {},
            "order": order or {"DataCadastro": "desc"},
            "paginacao": {"pagina": pagina, "quantidade": quantidade},
        }, separators=(",", ":"))

    @staticmethod
    def _items_from_response(data: Any) -> list[dict]:
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            return [v for k, v in data.items() if k.isdigit() and isinstance(v, dict)]
        return []

    def listar_clientes(self, *, bucket_corretor_id: int | None = None, data_desde: str | None = None,
                         quantidade: int = 50) -> list[Lead]:
        """Lista leads. Server-side filtra Corretor; data_desde é client-side."""
        filter_: dict[str, Any] = {}
        if bucket_corretor_id is not None:
            filter_["Corretor"] = str(bucket_corretor_id)

        pesquisa = self._build_search(
            fields=list(self.LISTAR_FIELDS_DEFAULT),
            filter_=filter_,
            quantidade=quantidade,
        )
        url = f"{self.base_url}/clientes/listar"
        params = {"key": self.api_key, "pesquisa": pesquisa}
        r = self._client.get(url, params=params)
        r.raise_for_status()
        items = self._items_from_response(r.json())

        leads: list[Lead] = []
        for raw in items:
            data_cad = raw.get("DataCadastro")
            if data_desde and data_cad and data_cad < data_desde:
                continue  # filtro client-side
            leads.append(Lead(
                codigo=str(raw.get("Codigo", "")),
                nome=raw.get("Nome") or "",
                veiculo_captacao=raw.get("VeiculoCaptacao"),
                data_cadastro=data_cad,
                corretor_id=int(raw["Corretor"]) if str(raw.get("Corretor") or "").isdigit() else None,
                raw=raw,
            ))
        log.info("Vista listar_clientes returned %d items (after data_desde filter)", len(leads))
        return leads

    def obter_detalhes(self, codigo: str) -> dict:
        """Detalhes de UM cliente — usar pra pegar Celular que não está no listar."""
        pesquisa = json.dumps({"fields": list(self.DETALHES_FIELDS_DEFAULT)}, separators=(",", ":"))
        url = f"{self.base_url}/clientes/detalhes"
        params = {"key": self.api_key, "cliente": codigo, "pesquisa": pesquisa}
        r = self._client.get(url, params=params)
        r.raise_for_status()
        return r.json()

    def enrich_lead_with_celular(self, lead: Lead) -> Lead:
        """Busca detalhes e popula lead.telefones se houver Celular."""
        try:
            det = self.obter_detalhes(lead.codigo)
            celular = (det.get("Celular") or "").strip()
            if celular:
                lead.telefones = [celular]
        except Exception as e:
            log.warning("falha enrich lead %s: %s", lead.codigo, e)
        return lead

    @staticmethod
    def normalize_phone(raw: str) -> str:
        return re.sub(r"\D", "", raw or "")
