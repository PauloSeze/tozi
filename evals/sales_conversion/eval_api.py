"""API HTTP mínima sobre o SQLite do eval — superfície pro Copilot do gerente.

Expõe os agregados de `analytics.report()` num endpoint que a Custom Tool
`consultar_analise_conversas` do Captain consome. Roda local na PAULAO
(127.0.0.1:8910), protegida por bearer token. Não é exposta publicamente —
o Captain (chatwoot) roda no mesmo host e chama via loopback.

Uso:
    EVAL_API_TOKEN=xxx uvicorn eval_api:app --host 127.0.0.1 --port 8910
"""
from __future__ import annotations

import os

from fastapi import FastAPI, Header, HTTPException
from dotenv import load_dotenv
from pathlib import Path

import analytics

load_dotenv(Path(__file__).parent / ".env")

API_TOKEN = os.getenv("EVAL_API_TOKEN", "")

app = FastAPI(title="Tozi Eval API", docs_url=None, redoc_url=None, openapi_url=None)


def _check_auth(authorization: str | None) -> None:
    if not API_TOKEN:
        raise HTTPException(status_code=500, detail="EVAL_API_TOKEN não configurado")
    expected = f"Bearer {API_TOKEN}"
    if authorization != expected:
        raise HTTPException(status_code=401, detail="token inválido")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/report")
def report(authorization: str | None = Header(default=None)) -> dict:
    _check_auth(authorization)
    return analytics.report()
