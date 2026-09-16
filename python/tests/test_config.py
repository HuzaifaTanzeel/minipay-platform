"""Config precedence: --config file, then env, then ~/.minipay/support.ini."""
from pathlib import Path

import pytest

from support_tool.config import ConfigError, load


def _write_ini(path: Path, dsn: str, extra: str = "") -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "[minipay]\n"
        f"db_dsn = {dsn}\n"
        f"{extra}",
        encoding="utf-8",
    )
    return path


def test_missing_dsn_raises(monkeypatch, tmp_path):
    monkeypatch.delenv("MINIPAY_DB_DSN", raising=False)
    monkeypatch.setattr("support_tool.config.Path.home", lambda: tmp_path)
    with pytest.raises(ConfigError, match="MINIPAY_DB_DSN"):
        load()


def test_env_beats_home_ini(monkeypatch, tmp_path):
    _write_ini(tmp_path / ".minipay" / "support.ini", "postgresql://home")
    monkeypatch.setattr("support_tool.config.Path.home", lambda: tmp_path)
    monkeypatch.setenv("MINIPAY_DB_DSN", "postgresql://env")
    cfg = load()
    assert cfg.db_dsn == "postgresql://env"


def test_cli_config_beats_env(monkeypatch, tmp_path):
    monkeypatch.setenv("MINIPAY_DB_DSN", "postgresql://env")
    monkeypatch.setattr("support_tool.config.Path.home", lambda: tmp_path)
    ini = _write_ini(tmp_path / "cli.ini", "postgresql://file")
    cfg = load(str(ini))
    assert cfg.db_dsn == "postgresql://file"


def test_missing_config_file_raises(monkeypatch, tmp_path):
    monkeypatch.setenv("MINIPAY_DB_DSN", "postgresql://env")
    monkeypatch.setattr("support_tool.config.Path.home", lambda: tmp_path)
    with pytest.raises(ConfigError, match="not found"):
        load(str(tmp_path / "nope.ini"))


def test_stuck_minutes_from_env(monkeypatch, tmp_path):
    monkeypatch.setenv("MINIPAY_DB_DSN", "postgresql://env")
    monkeypatch.setenv("MINIPAY_STUCK_MINUTES", "30")
    monkeypatch.setattr("support_tool.config.Path.home", lambda: tmp_path)
    cfg = load()
    assert cfg.stuck_minutes == 30
    assert cfg.timeout_s == 3.0
