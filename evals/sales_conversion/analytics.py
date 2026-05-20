"""Persistência SQLite + agregação dos resultados do eval.

Sem dependência externa (Supabase fica pra fase 3 se precisar). SQLite local
permite GROUP BY nas taxonomias — a base do 'copiloto do gerente'.

Uso:
    python analytics.py report          # agregações da base toda
    python analytics.py import resultados.jsonl   # popula a partir de JSONL
"""
from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from collections import Counter
from pathlib import Path

DB_PATH = Path(__file__).parent / "results" / "evals.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS eval_results (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  conversation_id INTEGER,
  evaluated_at TEXT,
  model TEXT,
  interest_level TEXT,
  intent_detected TEXT,
  funnel_stage TEXT,
  partner_sentiment TEXT,
  loss_trigger TEXT,
  analyst_observation TEXT,
  objections_json TEXT,
  agent_failures_json TEXT,
  handoff_json TEXT,
  raw_json TEXT,
  UNIQUE(conversation_id, evaluated_at)
);
"""


def connect(db_path: Path = DB_PATH) -> sqlite3.Connection:
    db_path.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.execute(SCHEMA)
    return conn


def save(result: dict, db_path: Path = DB_PATH) -> None:
    meta = result.get("_metadata", {})
    conn = connect(db_path)
    try:
        conn.execute(
            """INSERT OR IGNORE INTO eval_results
            (conversation_id, evaluated_at, model, interest_level, intent_detected,
             funnel_stage, partner_sentiment, loss_trigger, analyst_observation,
             objections_json, agent_failures_json, handoff_json, raw_json)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                meta.get("conversation_id"),
                meta.get("evaluated_at"),
                meta.get("model"),
                result.get("interest_level"),
                result.get("intent_detected"),
                result.get("funnel_stage"),
                result.get("partner_sentiment"),
                result.get("loss_trigger"),
                result.get("analyst_observation"),
                json.dumps(result.get("objections", []), ensure_ascii=False),
                json.dumps(result.get("agent_failures", []), ensure_ascii=False),
                json.dumps(result.get("handoff_quality", {}), ensure_ascii=False),
                json.dumps(result, ensure_ascii=False),
            ),
        )
        conn.commit()
    finally:
        conn.close()


def report(db_path: Path = DB_PATH) -> dict:
    conn = connect(db_path)
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT * FROM eval_results").fetchall()
    conn.close()

    total = len(rows)
    objection_counter = Counter()
    failure_counter = Counter()
    failure_by_persona = Counter()
    funnel = Counter()
    intent = Counter()
    interest = Counter()
    handoff_timing = Counter()

    for r in rows:
        funnel[r["funnel_stage"]] += 1
        intent[r["intent_detected"]] += 1
        interest[r["interest_level"]] += 1
        for obj in json.loads(r["objections_json"] or "[]"):
            objection_counter[obj.get("category", "?")] += 1
        for fail in json.loads(r["agent_failures_json"] or "[]"):
            failure_counter[fail.get("category", "?")] += 1
            failure_by_persona[fail.get("agent_persona", "?")] += 1
        h = json.loads(r["handoff_json"] or "{}")
        if h.get("happened") == "YES":
            handoff_timing[h.get("timing", "?")] += 1

    return {
        "total_conversas": total,
        "interesse": dict(interest),
        "intencao": dict(intent),
        "funil": dict(funnel),
        "top_objecoes": objection_counter.most_common(10),
        "top_falhas": failure_counter.most_common(10),
        "falhas_por_agente": dict(failure_by_persona),
        "handoff_timing": dict(handoff_timing),
    }


def print_report(db_path: Path = DB_PATH) -> None:
    rep = report(db_path)
    print(f"\n=== ANÁLISE DE CONVERSAS ({rep['total_conversas']} avaliadas) ===\n")
    print(f"Interesse:   {rep['interesse']}")
    print(f"Intenção:    {rep['intencao']}")
    print(f"Funil:       {rep['funil']}")
    print(f"\nTop objeções (por que NÃO converteu):")
    for cat, n in rep["top_objecoes"]:
        print(f"  {n:3}x  {cat}")
    print(f"\nTop falhas do agente:")
    for cat, n in rep["top_falhas"]:
        print(f"  {n:3}x  {cat}")
    print(f"\nFalhas por agente: {rep['falhas_por_agente']}")
    print(f"Handoff timing:    {rep['handoff_timing']}\n")


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("report")
    imp = sub.add_parser("import")
    imp.add_argument("jsonl", type=Path)
    args = parser.parse_args()

    if args.cmd == "report":
        print_report()
    elif args.cmd == "import":
        n = 0
        for line in args.jsonl.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            save(json.loads(line))
            n += 1
        print(f"importados {n} resultados", file=sys.stderr)
        print_report()


if __name__ == "__main__":
    main()
