from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


def _env(key: str, default: str | None = None, required: bool = False) -> str:
    val = os.getenv(key, default)
    if required and not val:
        raise RuntimeError(f"Missing required env var: {key}")
    return val or ""


@dataclass(frozen=True)
class Config:
    vista_base_url: str
    vista_api_key: str
    vista_bucket_lead_user_id: int

    spx_base_url: str
    spx_account_id: int
    spx_inbox_id: int
    spx_inbox_identifier: str
    spx_user_token: str

    followup_days: tuple[int, ...]
    followup_max_attempts: int

    tz: str
    dry_run: bool
    log_level: str


def load() -> Config:
    return Config(
        vista_base_url=_env("VISTA_BASE_URL", required=True),
        vista_api_key=_env("VISTA_API_KEY", required=True),
        vista_bucket_lead_user_id=int(_env("VISTA_BUCKET_LEAD_USER_ID", "20")),
        spx_base_url=_env("SPX_BASE_URL", required=True),
        spx_account_id=int(_env("SPX_ACCOUNT_ID", required=True)),
        spx_inbox_id=int(_env("SPX_INBOX_ID", required=True)),
        spx_inbox_identifier=_env("SPX_INBOX_IDENTIFIER", required=True),
        spx_user_token=_env("SPX_USER_TOKEN", required=True),
        followup_days=tuple(int(d.strip()) for d in _env("FOLLOWUP_DAYS", "1,3,7,14,30,60,90").split(",")),
        followup_max_attempts=int(_env("FOLLOWUP_MAX_ATTEMPTS", "4")),
        tz=_env("TZ", "America/Cuiaba"),
        dry_run=_env("DRY_RUN", "false").lower() == "true",
        log_level=_env("LOG_LEVEL", "INFO"),
    )
