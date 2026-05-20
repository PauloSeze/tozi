"""CLI: python -m engine <subcmd>"""
from __future__ import annotations

import argparse
import logging
import sys

from . import config
from .engine import Engine
from .spx import SpxClient


def main():
    parser = argparse.ArgumentParser(prog="engine", description="Tozi follow-up & prospecção")
    parser.add_argument("--dry-run", action="store_true", help="não envia nada, só loga o que faria")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("poll", help="SDR passivo: polling Vista + disparo")
    sub.add_parser("followup", help="follow-up D+N")
    sub.add_parser("bdr", help="BDR varredura > 90 dias")
    send_p = sub.add_parser("send", help="envia mensagem manual (debug)")
    send_p.add_argument("phone", help="+55... E.164")
    send_p.add_argument("message", help="texto da mensagem")

    args = parser.parse_args()

    cfg = config.load()
    logging.basicConfig(level=cfg.log_level, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

    dry_run = args.dry_run or cfg.dry_run
    engine = Engine(cfg)

    if args.cmd == "poll":
        stats = engine.poll_new_leads(dry_run=dry_run)
        print(stats)
    elif args.cmd == "followup":
        stats = engine.run_followup(dry_run=dry_run)
        print(stats)
    elif args.cmd == "bdr":
        stats = engine.run_bdr(dry_run=dry_run)
        print(stats)
    elif args.cmd == "send":
        with SpxClient(
            base_url=cfg.spx_base_url,
            account_id=cfg.spx_account_id,
            user_token=cfg.spx_user_token,
            inbox_id=cfg.spx_inbox_id,
            inbox_identifier=cfg.spx_inbox_identifier,
        ) as spx:
            phone_e164 = spx.normalize_phone_br(args.phone)
            contact = spx.search_contact_by_phone(phone_e164)
            if not contact:
                if dry_run:
                    print(f"[DRY] criaria contact + conv pra {phone_e164}")
                    return
                contact = spx.create_contact("Manual Test", phone_e164)
            if dry_run:
                print(f"[DRY] enviaria '{args.message}' pra {phone_e164}")
                return
            conv = spx.create_conversation(
                contact_id=contact.id,
                source_id=phone_e164.lstrip("+"),
                first_message=args.message,
            )
            print(f"created conv {conv.id}")
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
