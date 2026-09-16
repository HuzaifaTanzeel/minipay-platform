"""Configuration: --config file, then env, then ~/.minipay/support.ini, then defaults.

Never log credential values. Missing DSN is a ConfigError (exit 3), not a stack trace.
"""
from __future__ import annotations

import configparser
import os
from dataclasses import dataclass
from pathlib import Path


class ConfigError(Exception):
    """User-facing configuration problem (missing file, missing DSN, bad number)."""


@dataclass(frozen=True)
class Config:
    db_dsn: str
    api_url: str
    api_key: str | None
    timeout_s: float = 3.0
    stuck_minutes: int = 15


def _read_ini(path: Path) -> dict[str, str]:
    parser = configparser.ConfigParser()
    try:
        read = parser.read(path)
    except OSError as e:
        raise ConfigError(f"config error: cannot read {path}: {e}") from e
    if not read:
        return {}
    if not parser.has_section("minipay"):
        return {}
    return {k: v for k, v in parser.items("minipay") if v != ""}


def load(cli_config: str | None = None) -> Config:
    if cli_config:
        cli_path = Path(cli_config)
        if not cli_path.is_file():
            raise ConfigError(f"config error: --config file not found: {cli_config}")
        cli_ini = _read_ini(cli_path)
    else:
        cli_ini = {}

    home_ini = _read_ini(Path.home() / ".minipay" / "support.ini")

    def pick(env_name: str, ini_key: str, default: str | None = None) -> str | None:
        if ini_key in cli_ini:
            return cli_ini[ini_key]
        env = os.getenv(env_name)
        if env:
            return env
        if ini_key in home_ini:
            return home_ini[ini_key]
        return default

    dsn = pick("MINIPAY_DB_DSN", "db_dsn")
    if not dsn:
        raise ConfigError(
            "config error: MINIPAY_DB_DSN not set (env or ~/.minipay/support.ini)"
        )

    timeout_raw = pick("MINIPAY_TIMEOUT", "timeout", "3")
    stuck_raw = pick("MINIPAY_STUCK_MINUTES", "stuck_minutes", "15")
    try:
        timeout_s = float(timeout_raw)  # type: ignore[arg-type]
        stuck_minutes = int(stuck_raw)  # type: ignore[arg-type]
    except (TypeError, ValueError) as e:
        raise ConfigError("config error: timeout and stuck_minutes must be numbers") from e

    api_key = pick("MINIPAY_API_KEY", "api_key")
    api_url = pick("MINIPAY_API_URL", "api_url", "http://localhost:8000") or "http://localhost:8000"

    return Config(
        db_dsn=dsn,
        api_url=api_url.rstrip("/"),
        api_key=api_key,
        timeout_s=timeout_s,
        stuck_minutes=stuck_minutes,
    )
