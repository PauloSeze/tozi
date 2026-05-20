"""Eval em lote das conversas resolvidas — roda no cron semanal.

Lista conversas resolvidas no SPX, exporta o transcript de cada uma, roda o
LLM-judge e grava um JSONL por semana em results/. Não depende de Supabase
ainda (fase 2): saída local agregável depois.

Uso:
    python weekly_eval.py            # últimas resolvidas
    python weekly_eval.py --limit 50
"""
from __future__ import annotations

import argparse
import json
import os
from datetime import datetime
from pathlib import Path

import httpx
from dotenv import load_dotenv

import runner  # reusa eval_conversation + export-from-spx do runner.py
import analytics  # persistência SQLite + agregação

HERE = Path(__file__).parent
load_dotenv(HERE / ".env")

SPX_BASE_URL = os.getenv("SPX_BASE_URL", "https://paulo.chatspx.app")
SPX_ACCOUNT_ID = int(os.getenv("SPX_ACCOUNT_ID", "1"))
SPX_USER_TOKEN = os.getenv("SPX_USER_TOKEN", "")
RESULTS_DIR = HERE / "results"


def list_resolved_conversations(limit: int = 50) -> list[int]:
    url = f"{SPX_BASE_URL}/api/v1/accounts/{SPX_ACCOUNT_ID}/conversations"
    r = httpx.get(
        url,
        headers={"api_access_token": SPX_USER_TOKEN},
        params={"status": "resolved", "page": 1},
        timeout=30.0,
    )
    r.raise_for_status()
    payload = r.json().get("data", {}).get("payload", [])
    return [c["id"] for c in payload][:limit]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=50)
    args = parser.parse_args()

    RESULTS_DIR.mkdir(exist_ok=True)
    week = datetime.now().strftime("%Y-W%W")
    out_path = RESULTS_DIR / f"{week}.jsonl"

    ids = list_resolved_conversations(args.limit)
    print(f"[{datetime.now().isoformat()}] {len(ids)} conversas resolvidas pra avaliar")

    done = 0
    with out_path.open("a", encoding="utf-8") as out:
        for conv_id in ids:
            try:
                transcript = runner.export_from_spx(conv_id)
                if not transcript.strip():
                    continue
                result = runner.eval_conversation(transcript)
                result["_metadata"] = {
                    "evaluated_at": datetime.now().isoformat(),
                    "model": runner.MODEL,
                    "conversation_id": conv_id,
                }
                out.write(json.dumps(result, ensure_ascii=False) + "\n")
                analytics.save(result)
                done += 1
                print(f"  conv {conv_id} OK")
            except Exception as e:
                print(f"  conv {conv_id} ERR: {e}")

    print(f"[{datetime.now().isoformat()}] {done} avaliações gravadas em {out_path}")


if __name__ == "__main__":
    main()
