"""Runner standalone do eval Tozi Sales Conversion Diagnostics.

Não depende do framework iFood completo. Chama Claude API direto com o schema
estruturado e persiste JSONL.

Uso:
    python runner.py export-from-spx --conversation-id 18 > transcript.txt
    python runner.py eval --transcript transcript.txt
    python runner.py eval-batch --csv conversas.csv --out results.jsonl
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

import httpx
from dotenv import load_dotenv

load_dotenv()

HERE = Path(__file__).parent
PROMPT_PATH = HERE / "prompt.md"
SCHEMA_PATH = HERE / "schema.json"

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY") or ""
MODEL = os.getenv("EVAL_MODEL", "claude-sonnet-4-5")

SPX_BASE_URL = os.getenv("SPX_BASE_URL", "https://paulo.chatspx.app")
SPX_ACCOUNT_ID = int(os.getenv("SPX_ACCOUNT_ID", "1"))
SPX_USER_TOKEN = os.getenv("SPX_USER_TOKEN", "")


def load_prompt() -> str:
    return PROMPT_PATH.read_text(encoding="utf-8")


def load_schema() -> dict:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def schema_to_tool_definition(schema: dict) -> dict:
    """Converte o schema customizado pro formato esperado por Anthropic tool_use."""
    properties: dict = {}
    required: list[str] = []
    for field_name, spec in schema.items():
        properties[field_name] = _spec_to_jsonschema(spec)
        required.append(field_name)
    return {
        "name": "register_diagnostic",
        "description": "Registra o diagnóstico completo da conversa analisada.",
        "input_schema": {"type": "object", "properties": properties, "required": required},
    }


def _spec_to_jsonschema(spec: dict) -> dict:
    t = spec.get("type", "str")
    desc = spec.get("description", "")
    if t == "str":
        return {"type": "string", "description": desc}
    if t == "list[object]":
        sub = spec.get("sub_fields", {})
        return {
            "type": "array",
            "description": desc,
            "items": {
                "type": "object",
                "properties": {k: _spec_to_jsonschema(v) for k, v in sub.items()},
                "required": list(sub.keys()),
            },
        }
    if t == "object":
        sub = spec.get("sub_fields", {})
        return {
            "type": "object",
            "description": desc,
            "properties": {k: _spec_to_jsonschema(v) for k, v in sub.items()},
            "required": list(sub.keys()),
        }
    return {"type": "string", "description": desc}


def eval_conversation(transcript: str) -> dict:
    if not ANTHROPIC_API_KEY:
        raise RuntimeError("ANTHROPIC_API_KEY env var missing")

    prompt = load_prompt()
    schema = load_schema()
    tool = schema_to_tool_definition(schema)

    body = {
        "model": MODEL,
        "max_tokens": 4096,
        "system": prompt,
        "tools": [tool],
        "tool_choice": {"type": "tool", "name": "register_diagnostic"},
        "messages": [
            {"role": "user", "content": f"# Transcript\n\n{transcript}"}
        ],
    }

    r = httpx.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": ANTHROPIC_API_KEY,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        json=body,
        timeout=120.0,
    )
    r.raise_for_status()
    payload = r.json()

    for block in payload.get("content", []):
        if block.get("type") == "tool_use" and block.get("name") == "register_diagnostic":
            return block["input"]
    raise RuntimeError(f"No tool_use block in response: {payload}")


def export_from_spx(conversation_id: int) -> str:
    """Exporta uma conversa do SPX como transcript formatado."""
    url = f"{SPX_BASE_URL}/api/v1/accounts/{SPX_ACCOUNT_ID}/conversations/{conversation_id}/messages"
    r = httpx.get(url, headers={"api_access_token": SPX_USER_TOKEN}, timeout=30.0)
    r.raise_for_status()
    messages = r.json().get("payload", [])

    lines: list[str] = []
    for msg in messages:
        if msg.get("private"):
            continue  # nota privada não vai pro transcript
        if msg.get("content_attributes", {}).get("nps_survey"):
            continue
        sender_type = msg.get("sender_type", "")
        sender_name = (msg.get("sender") or {}).get("name", "?")
        if sender_type == "Contact":
            speaker = "Cliente"
        elif sender_type == "AgentBot" or msg.get("message_type") in (1, "outgoing") and not msg.get("private"):
            # tenta identificar agente IA pelo nome do bot vs nome do usuário humano
            speaker = sender_name or "IA"
        else:
            speaker = sender_name or "IA"
        content = (msg.get("content") or "").strip()
        if not content:
            continue
        lines.append(f"[{speaker}]: {content}")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Tozi Sales Conversion Eval Runner")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_export = sub.add_parser("export-from-spx", help="Exporta transcript de uma conversa do SPX")
    p_export.add_argument("--conversation-id", required=True, type=int)

    p_eval = sub.add_parser("eval", help="Roda eval em uma conversa")
    p_eval.add_argument("--transcript", required=True, type=Path, help="Path pro arquivo .txt do transcript")
    p_eval.add_argument("--out", type=Path, default=None, help="Path pra salvar JSON (default: stdout)")

    p_batch = sub.add_parser("eval-batch", help="Roda eval em lote a partir de CSV")
    p_batch.add_argument("--csv", required=True, type=Path)
    p_batch.add_argument("--out", required=True, type=Path)

    args = parser.parse_args()

    if args.cmd == "export-from-spx":
        print(export_from_spx(args.conversation_id))

    elif args.cmd == "eval":
        transcript = args.transcript.read_text(encoding="utf-8")
        result = eval_conversation(transcript)
        result["_metadata"] = {"evaluated_at": datetime.now().isoformat(), "model": MODEL}
        output = json.dumps(result, ensure_ascii=False, indent=2)
        if args.out:
            args.out.write_text(output, encoding="utf-8")
            print(f"saved → {args.out}", file=sys.stderr)
        else:
            print(output)

    elif args.cmd == "eval-batch":
        import csv
        with args.csv.open("r", encoding="utf-8") as f, args.out.open("w", encoding="utf-8") as out:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader, 1):
                transcript = row.get("formatted_conversation", "")
                if not transcript:
                    continue
                try:
                    result = eval_conversation(transcript)
                    result["_metadata"] = {
                        "evaluated_at": datetime.now().isoformat(),
                        "model": MODEL,
                        "row_index": i,
                        **{k: v for k, v in row.items() if k != "formatted_conversation"},
                    }
                    out.write(json.dumps(result, ensure_ascii=False) + "\n")
                    print(f"row {i} OK", file=sys.stderr)
                except Exception as e:
                    print(f"row {i} ERR: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
